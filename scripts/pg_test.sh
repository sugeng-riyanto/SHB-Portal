#!/usr/bin/env bash
# Run the Django test suite against a real PostgreSQL engine, without root.
#
# This image has no PostgreSQL, no apt package lists and no sudo (the
# "no new privileges" flag blocks it), so the script uses the binaries bundled with the
# `pgserver` pip package and runs a cluster as the current user in a directory outside the
# repository. Nothing in the repository is modified and no production database is touched.
#
# Usage:
#   ./scripts/pg_test.sh                        # whole portal suite on PostgreSQL
#   ./scripts/pg_test.sh portal.tests.ConcurrentProofVerificationTests
#   KEEP_RUNNING=1 ./scripts/pg_test.sh         # leave the cluster up afterwards
#   SHB_PGDATA=$HOME/shb-pgdata-fresh SHB_PGPORT=55433 ./scripts/pg_test.sh
#
# Overridable environment: PY, SHB_PGDATA, SHB_PGPORT, SHB_PGSOCKET, SHB_PGDB, SHB_PGUSER,
# SHB_PGPASSWORD, KEEP_RUNNING.
#
# Why the Unix socket: config/settings.py hardcodes OPTIONS {'sslmode': 'require'}. The
# bundled PostgreSQL build is compiled without SSL ("SSL is not supported by this build"),
# so a TCP connection with sslmode=require cannot work. libpq does not attempt TLS over a
# Unix socket, so POSTGRES_HOST points at the socket directory and the project's settings
# stay unmodified. See docs/POSTGRES_TESTING.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# pgserver (via platformdirs) warns on every import when XDG_RUNTIME_DIR is unset.
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/runtime-$(id -u)}"

PY="${PY:-$ROOT/.venv/bin/python}"
PGDATA="${SHB_PGDATA:-$HOME/shb-pgdata}"
PGPORT="${SHB_PGPORT:-55432}"
PGSOCKET="${SHB_PGSOCKET:-/tmp}"
PGDB="${SHB_PGDB:-shb}"
PGUSER="${SHB_PGUSER:-shb}"
PGPASSWORD="${SHB_PGPASSWORD:-local-test-only}"

# A restored worktree has no virtualenv, or an empty one; make it usable so a single
# command is enough. Dependencies are not installed automatically on restore.
if [ ! -x "$PY" ]; then
  echo ">> no virtualenv at $PY; creating it"
  python3 -m venv "$ROOT/.venv"
  "$PY" -m pip install --quiet --upgrade pip
  "$PY" -m pip install --quiet -r "$ROOT/requirements.txt"
elif ! "$PY" -c 'import django, openpyxl, PIL' >/dev/null 2>&1; then
  echo ">> virtualenv exists but dependencies are missing; installing requirements.txt"
  "$PY" -m pip install --quiet -r "$ROOT/requirements.txt"
fi

if ! "$PY" -c 'import pgserver' >/dev/null 2>&1; then
  echo ">> installing pgserver (bundled test-only PostgreSQL binaries)"
  "$PY" -m pip install --quiet pgserver
fi

PGBIN="$("$PY" -c "import glob,os,pgserver;b=os.path.dirname(pgserver.__file__);f=glob.glob(os.path.join(b,'**','bin','initdb'),recursive=True);print(os.path.dirname(f[0]) if f else '')")"
if [ -z "$PGBIN" ] || [ ! -x "$PGBIN/initdb" ]; then
  echo "error: could not find the PostgreSQL binaries bundled with pgserver" >&2
  exit 1
fi

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo ">> initdb $PGDATA"
  if ! "$PGBIN/initdb" -D "$PGDATA" -U "$PGUSER" -E UTF8 --auth=trust >"$PGDATA.initdb.log" 2>&1; then
    tail -20 "$PGDATA.initdb.log" >&2
    exit 1
  fi
fi

started=0
if "$PGBIN/pg_ctl" -D "$PGDATA" status >/dev/null 2>&1; then
  echo ">> cluster already running: $PGDATA"
else
  # A killed runner leaves postmaster.pid behind even though nothing is listening.
  if [ -f "$PGDATA/postmaster.pid" ]; then
    stale_pid="$(head -1 "$PGDATA/postmaster.pid" 2>/dev/null || true)"
    if [ -n "$stale_pid" ] && ! kill -0 "$stale_pid" 2>/dev/null; then
      echo ">> removing stale postmaster.pid (pid $stale_pid is gone)"
      rm -f "$PGDATA/postmaster.pid"
    fi
  fi
  echo ">> starting cluster on port $PGPORT (socket $PGSOCKET)"
  "$PGBIN/pg_ctl" -D "$PGDATA" \
    -o "-p $PGPORT -c listen_addresses=127.0.0.1 -c unix_socket_directories=$PGSOCKET" \
    -l "$PGDATA/server.log" start >/dev/null
  started=1
  for _ in $(seq 1 30); do
    "$PGBIN/pg_isready" -h "$PGSOCKET" -p "$PGPORT" -q && break
    sleep 1
  done
fi

if ! "$PGBIN/pg_isready" -h "$PGSOCKET" -p "$PGPORT" >/dev/null; then
  echo "error: PostgreSQL is not accepting connections" >&2
  tail -20 "$PGDATA/server.log" >&2 || true
  exit 1
fi

if ! "$PGBIN/psql" -h "$PGSOCKET" -p "$PGPORT" -U "$PGUSER" -d postgres -Atc \
      "select 1 from pg_database where datname = '$PGDB'" | grep -q 1; then
  echo ">> creating database $PGDB"
  "$PGBIN/createdb" -h "$PGSOCKET" -p "$PGPORT" -U "$PGUSER" -O "$PGUSER" "$PGDB"
fi

TARGETS=("$@")
[ "${#TARGETS[@]}" -eq 0 ] && TARGETS=(portal)
echo ">> manage.py test ${TARGETS[*]} (PostgreSQL on $PGSOCKET:$PGPORT)"
status=0
POSTGRES_HOST="$PGSOCKET" \
POSTGRES_PORT="$PGPORT" \
POSTGRES_DB="$PGDB" \
POSTGRES_USER="$PGUSER" \
POSTGRES_PASSWORD="$PGPASSWORD" \
  "$PY" manage.py test "${TARGETS[@]}" || status=$?

if [ "$started" = 1 ] && [ "${KEEP_RUNNING:-0}" != 1 ]; then
  echo ">> stopping cluster (set KEEP_RUNNING=1 to keep it running)"
  "$PGBIN/pg_ctl" -D "$PGDATA" stop >/dev/null
fi

exit "$status"
