#!/usr/bin/env bash
# Verifikasi pasca-deploy portal SHB.
#
# Memastikan dua hal yang mudah salah setelah nginx diganti:
#   1. port 80 mengalihkan ke HTTPS (301/308), bukan melayani langsung atau 404;
#   2. port 443 menjawab 200 dari APLIKASI, bukan halaman galat nginx.
#
# Pemakaian:
#   ./deploy/verify_deploy.sh                       # host default
#   ./deploy/verify_deploy.sh --host portal.contoh.id
#   ./deploy/verify_deploy.sh --loopback            # sekalian uji 127.0.0.1 dari server
#   ./deploy/verify_deploy.sh --https-url http://127.0.0.1:3000 --skip-redirect
#
# Keluar 0 bila semua lulus, 1 bila ada yang gagal, 2 bila argumen salah.
set -uo pipefail

HOST="portal.scangrade.web.id"
HTTP_URL=""
HTTPS_URL=""
SKIP_REDIRECT=0
LOOPBACK=0
FAILS=0
CHECKS=0
TMPD="$(mktemp -d)"
trap 'rm -rf "$TMPD"' EXIT

while [ $# -gt 0 ]; do
  case "$1" in
    --host) HOST="${2:?--host butuh nilai}"; shift 2 ;;
    --host=*) HOST="${1#*=}"; shift ;;
    --http-url) HTTP_URL="${2:?--http-url butuh nilai}"; shift 2 ;;
    --https-url) HTTPS_URL="${2:?--https-url butuh nilai}"; shift 2 ;;
    --skip-redirect) SKIP_REDIRECT=1; shift ;;
    --loopback) LOOPBACK=1; shift ;;
    -h|--help) sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) printf 'argumen tidak dikenal: %s\n' "$1" >&2; exit 2 ;;
  esac
done
HTTP_URL="${HTTP_URL:-http://$HOST}"
HTTPS_URL="${HTTPS_URL:-https://$HOST}"

pass() { CHECKS=$((CHECKS+1)); printf '  PASS  %s\n' "$*"; }
fail() { CHECKS=$((CHECKS+1)); FAILS=$((FAILS+1)); printf '  FAIL  %s\n' "$*"; }
note() { printf '        %s\n' "$*"; }
head2() { printf '\n%s\n' "$*"; }

CODE=000
BODY="$TMPD/body"
HDRS="$TMPD/hdrs"

fetch() {
  local url="$1"
  : > "$BODY"; : > "$HDRS"
  CODE="$(curl -sS -o "$BODY" -D "$HDRS" -w '%{http_code}' --max-time 20 "$url" 2>"$TMPD/err" || echo 000)"
  if [ "$CODE" = "000" ]; then note "curl gagal: $(head -n1 "$TMPD/err" 2>/dev/null)"; fi
}
hdr() { grep -i "^$1:" "$HDRS" 2>/dev/null | tr -d '\r' | sed "s/^$1:[[:space:]]*//I" | head -n1; }
size() { wc -c < "$BODY" 2>/dev/null || echo 0; }
is_nginx_error() { grep -qiE '<center>nginx|<title>(403 Forbidden|404 Not Found|502 Bad Gateway|500 Internal Server Error)</title>' "$BODY"; }
has_app_marker() { grep -qiE 'SHB Portal|id="main-content"|csrfmiddlewaretoken|/static/portal/' "$BODY"; }

printf 'Verifikasi deploy SHB Portal\n  HTTP  : %s\n  HTTPS : %s\n  waktu : %s\n' "$HTTP_URL" "$HTTPS_URL" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# --- 1. Port 80 harus mengalihkan ke HTTPS --------------------------------
if [ "$SKIP_REDIRECT" = "1" ]; then
  note "lewati pemeriksaan redirect port 80 (--skip-redirect)"
else
  head2 "1. Port 80 -> HTTPS"
  fetch "$HTTP_URL/"
  loc="$(hdr location)"
  case "$CODE" in
    301|308)
      if printf '%s' "$loc" | grep -qi '^https://'; then
        pass "port 80 menjawab $CODE ke $loc"
      else
        fail "port 80 menjawab $CODE tetapi Location bukan HTTPS: '$loc'"
      fi ;;
    200) fail "port 80 melayani 200 langsung; seharusnya mengalihkan ke HTTPS" ;;
    404) fail "port 80 menjawab 404: blok port 80 untuk host ini tidak dimuat" ;;
    403) fail "port 80 menjawab 403 ($(size) byte); ada aturan yang menolak" ;;
    *)   fail "port 80 menjawab $CODE, bukan 301/308" ;;
  esac
fi

# --- 2. HTTPS harus menjawab dari aplikasi --------------------------------
head2 "2. HTTPS menjawab dari aplikasi"
fetch "$HTTPS_URL/"
if [ "$CODE" = "200" ]; then pass "root menjawab 200"; else fail "root menjawab $CODE ($(size) byte)"; fi

if is_nginx_error; then
  fail "badan respons adalah halaman galat nginx, bukan aplikasi"
else
  pass "bukan halaman galat nginx"
fi

srv="$(hdr server)"
if [ -z "$srv" ]; then
  pass "header Server tidak diisi (lazim untuk aplikasi di balik proxy)"
elif printf '%s' "$srv" | grep -qi nginx; then
  fail "header Server masih '$srv': permintaan tidak sampai ke aplikasi"
else
  pass "header Server '$srv' (bukan nginx)"
fi

if has_app_marker; then pass "badan memuat penanda aplikasi SHB Portal"; else fail "tidak ada penanda aplikasi di badan respons"; fi

# --- 3. Halaman login dirender Django ------------------------------------
head2 "3. Halaman login"
fetch "$HTTPS_URL/accounts/login/"
if [ "$CODE" = "200" ]; then pass "/accounts/login/ menjawab 200"; else fail "/accounts/login/ menjawab $CODE"; fi
if grep -q 'csrfmiddlewaretoken' "$BODY"; then pass "form login memuat token CSRF (view Django berjalan)"; else fail "token CSRF tidak ditemukan; halaman bukan dari Django"; fi

# --- 4. Berkas statis tersaji -------------------------------------------
head2 "4. Berkas statis"
fetch "$HTTPS_URL/static/portal/app.css"
ct="$(hdr content-type)"
if [ "$CODE" = "200" ]; then pass "app.css menjawab 200"; else fail "app.css menjawab $CODE"; fi
case "$ct" in
  *css*) pass "Content-Type $ct" ;;
  *) fail "Content-Type '$ct' bukan CSS" ;;
esac

# --- 5. Halaman terlindungi mengalihkan ke login -------------------------
head2 "5. Halaman terlindungi"
fetch "$HTTPS_URL/dashboard/"
loc="$(hdr location)"
case "$CODE" in
  302|303) if printf '%s' "$loc" | grep -q '/accounts/login'; then
             pass "/dashboard/ tanpa sesi mengalihkan ke login"
           else fail "/dashboard/ mengalihkan ke '$loc', bukan ke login"; fi ;;
  200) fail "/dashboard/ menjawab 200 tanpa sesi: halaman terlindungi terbuka" ;;
  403) fail "/dashboard/ menjawab 403 dari nginx, bukan dari aplikasi" ;;
  *)   fail "/dashboard/ menjawab $CODE" ;;
esac

# --- 6. Opsional: uji dari dalam server ----------------------------------
if [ "$LOOPBACK" = "1" ]; then
  head2 "6. Loopback dari server"
  c="$(curl -sS -o "$TMPD/lb" -w '%{http_code}' --max-time 10 -H "Host: $HOST" http://127.0.0.1/ 2>/dev/null || echo 000)"
  if [ "$c" = "301" ] || [ "$c" = "308" ]; then pass "loopback port 80 -> $c"; else fail "loopback port 80 -> $c"; fi
  c="$(curl -sk -o "$TMPD/lbs" -w '%{http_code}' --max-time 10 -H "Host: $HOST" https://127.0.0.1/ 2>/dev/null || echo 000)"
  if [ "$c" = "200" ]; then pass "loopback port 443 -> 200"; else fail "loopback port 443 -> $c"; fi
fi

# --- Ringkasan ------------------------------------------------------------
printf '\n%s dari %s pemeriksaan lulus\n' "$((CHECKS-FAILS))" "$CHECKS"
if [ "$FAILS" -gt 0 ]; then
  printf '\nPetunjuk berdasarkan pola kegagalan:\n'
  printf '  - port 80 menjawab 404 -> blok port 80 host ini belum dimuat: periksa sites-enabled/include, lalu reload.\n'
  printf '  - port 443 menjawab 403 dengan badan ~162 byte -> masih ada blok lama berisi deny/return 403.\n'
  printf '  - port 443 menjawab 502 -> upstream mati: periksa unit systemd gunicorn dan socket-nya.\n'
  printf '  - header Server masih nginx -> proxy_pass/lokasi belum diarahkan ke aplikasi.\n'
  printf '  - 200 tetapi tanpa penanda aplikasi -> root dilayani berkas statis atau halaman lain.\n'
  exit 1
fi
printf 'Deploy terverifikasi.\n'
