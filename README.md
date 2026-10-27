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
python manage.py runserver
```

Buka `http://127.0.0.1:8000/`. Panel super admin ada di `/admin/`. Akses portal per peran memerlukan akun serta hubungan sekolah, kelas, atau wali yang sesuai. Panduan instalasi ini menggunakan SQLite lokal, bukan database produksi.

## Pengujian

```bash
python manage.py test portal
```

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
