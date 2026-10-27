# SHB Portal

Portal informasi pembayaran dan komunikasi untuk Sekolah Harapan Bangsa. Mendukung rancangan enam peran: super admin, admin sekolah, kepala sekolah, yayasan, wali kelas, dan orang tua/wali.

> **Status: pengembangan, belum siap produksi.** Jangan gunakan data murid asli atau buka ke publik sebelum autentikasi, keamanan, integrasi, dan uji staging selesai.

## Yang tersedia saat ini

- Login/logout Django dan dashboard awal yang membatasi data berdasarkan sekolah, penugasan kelas, serta hubungan wali–murid. Kepala sekolah dan yayasan melihat agregat awal; super admin dapat mengelola sekolah dan penugasan melalui Django admin.
- Admin mengelola data murid, pencarian dan ekspor XLSX; kepala sekolah mengelola rekening dan ekspor XLSX sesuai lingkup.
- Unduh template dan **preview awal** impor tagihan XLSX. Preview belum mencocokkan data atau menyimpan tagihan.
- Wali mengunggah bukti transfer; admin memverifikasi setelah pemeriksaan. Akses foto dibatasi sesuai peran dan sekolah.
- Pesan individual dari admin ke inbox wali; SMTP opsional dengan status diterima server atau gagal. SMTP dinonaktifkan secara default.
- Dua template email pembayaran Indonesia/English; frontend awal responsif, light/dark, CSS dan JavaScript lokal.

Fitur ini masih fondasi. Pembatasan dan integritas perlu diuji menyeluruh pada PostgreSQL/Supabase; hasil lokal SQLite bukan bukti kesiapan produksi.

## Jalankan di PC untuk pengembangan

Persyaratan: Python 3.10 atau lebih baru dan Git. Gunakan data contoh.

```bash
git clone https://github.com/sugeng-riyanto/SHB-Portal.git
cd SHB-Portal
python -m venv .venv
```

Aktifkan lingkungan:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Kemudian:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo   # opsional: data contoh sintetis untuk preview
python manage.py runserver
```

Buka `http://127.0.0.1:8000/`. Panel super admin ada di `/admin/`. Akses portal per peran memerlukan akun serta hubungan sekolah, kelas, atau wali yang sesuai. Panduan instalasi ini menggunakan SQLite lokal, bukan database produksi.

## Pengujian

```bash
python manage.py test portal
```

Untuk menjalankan suite yang sama pada PostgreSQL sungguhan (tanpa root, satu perintah):

```bash
./scripts/pg_test.sh
```

Lihat [panduan uji PostgreSQL](docs/POSTGRES_TESTING.md) untuk prasyarat, skip yang disengaja dan batasannya.

```powershell
# Windows PowerShell: tes aturan domain
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
```

```bash
# Linux / macOS: tes aturan domain
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Konfigurasi dan Supabase

Lihat [.env.example](.env.example) dan [panduan Supabase](docs/SUPABASE_SETUP.md). Pengaturan dibaca dari **environment proses**; aplikasi belum otomatis membaca file `.env`. Jangan masukkan password atau API key ke Git atau chat.

Koneksi PostgreSQL TLS dapat dikonfigurasi, tetapi **Supabase Auth dan kebijakan RLS per peran belum diimplementasikan**. SQL hardening adalah rancangan deny-by-default yang belum diuji pada Supabase. Jangan jalankan migrasi pada proyek yang digunakan aplikasi lain tanpa identifikasi dan review.

Untuk SMTP, isi environment server sesuai panduan, lalu aktifkan `SHB_EMAIL_ENABLED=1` hanya setelah pengujian dengan alamat uji. Status diterima server tidak menjamin email sampai ke inbox atau dibaca. UI pengisian secret super admin dan koneksi Midtrans/WhatsApp belum aktif.

## Pekerjaan yang masih diperlukan

- Supabase Auth, aktivasi/reset akun, RLS dan pengujian lintas peran dengan database nyata.
- Impor final dan deduplikasi, pengelolaan wali/sibling, tahun ajaran dan kenaikan kelas, serta pengumuman.
- Bukti transfer: edit/tarik, audit, penyimpanan privat dan pengujian konkurensi PostgreSQL.
- Pengiriman massal, antrean, verifikasi alamat, kebijakan privasi, SMTP nyata dan integrasi WhatsApp/Midtrans.
- Dashboard semua peran, terjemahan lengkap, pengujian visual berbagai perangkat, backup/restore, monitoring dan pemeriksaan keamanan.
- Konfigurasi HTTPS, hosting static files (`collectstatic`), proses server dan uji staging sebelum rilis.

Baca [konstitusi proyek](docs/PROJECT_CONSTITUTION.md), [matriks RBAC](docs/RBAC_MATRIX.md), [pelindungan data](docs/PRIVACY_PDP.md), [release gates](docs/RELEASE_GATES.md), dan [status pekerjaan](docs/AI_HANDOFF.md).

### Akun demo lokal
Setelah migrasi, jalankan `python manage.py seed_demo` untuk membuat akun uji pada SQLite development. Email login: `superadmin@shb.sch.id`, `admin@shb.sch.id`, `kepala@shb.sch.id`, `yayasan@shb.sch.id`, `walikelas@shb.sch.id`, dan `ortu@shb.sch.id`; password dummy: `DemoSHB!2026`. Perintah juga mengisi data contoh: satu sekolah (`Sekolah Harapan Bangsa (contoh)`), tahun ajaran 2026/2027, kelas 7A dan 10N, tiga murid beserta wali, tiga tagihan dan satu rekening, agar dashboard preview tidak kosong. Semua data bersifat sintetis. Perintah tidak mengubah akun atau data yang sudah ada, dan ditolak di lingkungan produksi maupun PostgreSQL. Jangan gunakan akun/password ini pada server publik.

### Preview lokal: form POST 403 "CSRF token missing" padahal token ada
Jika login menampilkan `403 CSRF token missing` sementara halaman login jelas memuat `csrfmiddlewaretoken`, cookie `csrftoken` terkirim, dan origin sudah terdaftar di `DJANGO_CSRF_TRUSTED_ORIGINS`, penyebabnya biasanya badan request, bukan CSRF: proxy preview mengirim ulang POST dengan `Transfer-Encoding: chunked`, dan server pengembangan WSGI bawaan `runserver` tidak mendekode badan chunked sehingga `request.POST` kosong. Jalankan preview dengan server ASGI:

```bash
python -m pip install daphne   # dev saja, bukan kebutuhan produksi
python manage.py runserver
```

Bila `daphne` tersedia, `config/settings.py` mengaktifkannya otomatis dan `runserver` menjadi ASGI; tanpa `daphne` server WSGI tetap berjalan. Jangan mengubah atau menonaktifkan CSRF. Tandanya terlihat di log: baris `code 400, message Bad request syntax ('88')` tepat setelah 403 — angka itu ukuran chunk dalam heksadesimal, bukan permintaan sungguhan.

### Preview HTTPS: jika login menampilkan CSRF 403
Set `DJANGO_CSRF_TRUSTED_ORIGINS` pada environment server ke origin HTTPS yang tepat, misalnya `https://preview.example.test` (tanpa `/accounts/login/` dan tanpa garis miring terakhir), dan pastikan host juga ada di `DJANGO_ALLOWED_HOSTS`. Restart aplikasi setelah mengganti environment, kemudian muat ulang halaman login. Jangan gunakan wildcard domain atau mematikan CSRF. Jika berada di belakang reverse proxy, pengaturan proxy tepercaya harus sesuai setup deployment; jangan aktifkan header forwarding dari jaringan yang tidak dipercaya.
