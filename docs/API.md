# Kontrak API awal

Semua endpoint di bawah adalah rancangan, bukan endpoint yang sudah tersedia. HTTPS, autentikasi dan otorisasi server berlaku; paginasi dan filter mengikuti lingkup peran. Kesalahan 400 validasi, 401 autentikasi, 403 izin, 404 sumber tidak tersedia, 409 konflik, 429 pembatasan.

| Metode | Rute usulan | Tujuan |
|---|---|---|
| GET | /api/me | profil dan peran yang berlaku |
| GET/POST | /api/students | daftar sesuai lingkup / tambah |
| GET/PATCH | /api/students/{id} | detail / ubah |
| POST | /api/imports/preview | unggah dan validasi, tanpa commit atau email |
| POST | /api/imports/{id}/commit | commit baris dipilih; idempotency key |
| GET | /api/invoices | daftar sesuai lingkup |
| POST | /api/invoices/{id}/payments | catat pembayaran berotorisasi dan reference unik |
| POST | /api/academic-years/{id}/promotion-preview | preview kenaikan |
| POST | /api/promotions/{id}/commit | konfirmasi kenaikan idempotent |
| GET/POST | /api/announcements | daftar sesuai sasaran / buat |
| POST | /api/notifications/{id}/retry | kirim ulang terkendali untuk kegagalan |
| GET | /api/dashboard | metrik sesuai role, periode dan scope |

Aktivasi dan reset memakai alur Supabase Auth; finalisasi kontrak setelah memilih integrasi. Audit tindakan tulis, lindungi CSRF untuk autentikasi cookie, validasi server, batas ukuran dan catat correlation ID.
