# Uji pada PostgreSQL

Panduan menjalankan suite Django pada mesin PostgreSQL sungguhan, bukan hanya SQLite. Hasil
SQLite bukan bukti kesiapan produksi: urutan `serial`, kunci baris, dan constraint hanya
terbukti pada mesin nyata.

## Ringkas

```bash
./scripts/pg_test.sh
```

Satu perintah ini menyiapkan lingkungan, menjalankan `manage.py test portal` pada
PostgreSQL, lalu mematikan cluster. Untuk menjalankan satu tes:

```bash
./scripts/pg_test.sh portal.tests.ConcurrentProofVerificationTests
```

Biarkan cluster hidup untuk pemeriksaan manual:

```bash
KEEP_RUNNING=1 ./scripts/pg_test.sh
```

## Prasyarat

- Python 3.10+ dan `python3-venv`. Skrip membuat `.venv` dan memasang
  `requirements.txt` sendiri bila venv belum ada, sehingga worktree yang baru di-restore
  bisa langsung dipakai.
- Jaringan ke PyPI untuk memasang `pgserver` (paket ini membawa binari PostgreSQL).
- **Tidak perlu root.** Image ini menolak `sudo` (`no-new-privileges`) dan tidak punya
  daftar paket apt, jadi PostgreSQL tidak dipasang sebagai layanan sistem.

## Apa yang dijalankan skrip

1. Membuat `.venv` dan memasang `requirements.txt` bila belum ada.
2. Memasang `pgserver` bila belum ada dan mencari binari `initdb`/`pg_ctl` di dalamnya.
3. `initdb` di `$SHB_PGDATA` (default `$HOME/shb-pgdata`) dengan autentikasi `trust`,
   hanya bila direktori itu belum berisi cluster.
4. Menjalankan cluster dengan `pg_ctl` pada `$SHB_PGPORT` (default `55432`), mendengarkan
   `127.0.0.1` dan socket di `$SHB_PGSOCKET` (default `/tmp`).
5. Membuat database `$SHB_PGDB` (default `shb`) bila belum ada.
6. Menjalankan `manage.py test` dengan `POSTGRES_*` diarahkan ke cluster itu.
7. Mematikan cluster bila skrip yang menyalakannya (kecuali `KEEP_RUNNING=1`).

Variabel yang bisa diganti: `PY`, `SHB_PGDATA`, `SHB_PGPORT`, `SHB_PGSOCKET`, `SHB_PGDB`,
`SHB_PGUSER`, `SHB_PGPASSWORD`, `KEEP_RUNNING`.

## Mengapa lewat socket Unix

`config/settings.py` mengunci `OPTIONS: {'sslmode': 'require'}` untuk PostgreSQL. Binari
`pgserver` dikompilasi **tanpa dukungan SSL** (`SSL is not supported by this build`), jadi
koneksi TCP dengan `sslmode=require` tidak mungkin di mesin ini. libpq tidak mencoba TLS
pada socket Unix, sehingga skrip mengarahkan `POSTGRES_HOST` ke direktori socket dan
pengaturan proyek tidak perlu diubah sama sekali.

Konsekuensinya: **jalur produksi Supabase (TCP + TLS) tetap belum terverifikasi** oleh
pengujian ini. Yang terbukti adalah perilaku mesin PostgreSQL pada tingkat transaksi,
constraint dan penguncian.

## Hasil yang diharapkan

| Perintah | SQLite | PostgreSQL |
|---|---|---|
| `manage.py test portal` | lulus; 2 skip | lulus; 5 skip |
| `PYTHONPATH=src python -m unittest discover -s tests` | 5 lulus | 5 lulus (tidak memakai database) |

Skip yang disengaja, bukan lulus palsu:

- **Pada PostgreSQL**: tes `seed_demo` di-skip karena perintah itu menjaga aturan hanya
  SQLite pengembangan (menolak `SHB_ENV=production` dan engine non-SQLite).
- **Pada SQLite**: tes konkurensi di-skip karena SQLite mengunci seluruh database dan
  mengabaikan `SELECT ... FOR UPDATE`, sehingga dua penulis bersamaan tidak bisa diuji.

## Membersihkan

Binari PostgreSQL ada di dalam `.venv`; ambil `pg_ctl`-nya lewat `pgserver`:

```bash
PGBIN="$(.venv/bin/python -c "import glob,os,pgserver;b=os.path.dirname(pgserver.__file__);print(os.path.dirname(glob.glob(os.path.join(b,'**','bin','pg_ctl'),recursive=True)[0]))")"
"$PGBIN/pg_ctl" -D "$HOME/shb-pgdata" stop      # hentikan cluster yang masih hidup
rm -rf "$HOME/shb-pgdata" "$HOME/shb-pgdata.initdb.log"   # hapus seluruh data uji
```

Direktori data berada di luar repositori, jadi tidak ada berkas uji yang ikut ter-commit.
Cluster yang dibuat skrip ini hanya berisi data sintetis dari suite tes.

## Batasan

- Versi mesin adalah PostgreSQL yang dibawa `pgserver` (terakhir diuji 16.2); Supabase dapat
  memakai major version lain sehingga perilaku spesifik versi belum dikonfirmasi.
- Tidak menguji RLS Supabase, `deploy/supabase_hardening.sql`, migrasi pada proyek Supabase,
  maupun TLS/`sslmode=require` melalui TCP.
- Bukan pengganti lingkungan staging terisolasi dan tidak boleh dipakai dengan data murid
  nyata.

## Penanganan masalah- **`error: PostgreSQL is not accepting connections`** — lihat `$SHB_PGDATA/server.log`. Port yang bentrok atau `postmaster.pid` yang basi adalah penyebab paling umum; pilih port lain dengan `SHB_PGPORT=55433`.
- **`pg_ctl: another server might be running`** — sisa `postmaster.pid` dari runner yang dimatikan. Skrip memeriksa `pg_ctl status`, menghapus pid file basi itu bila prosesnya sudah tidak ada, lalu menyalakan cluster; bila prosesnya memang masih hidup, hentikan dulu dengan perintah di bagian Membersihkan.
- **`port is already in use`** — cluster lain masih berjalan pada port itu. Hentikan dengan
  `pg_ctl -D <direktori data> stop` atau pakai `SHB_PGPORT` berbeda.
- **`could not find the PostgreSQL binaries bundled with pgserver`** — pasang ulang dengan
  `.venv/bin/python -m pip install --force-reinstall pgserver`.
