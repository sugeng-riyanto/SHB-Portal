# Serah terima agen

Tanggal: 27 Oktober 2026. Status: spesifikasi awal saja; tidak ada repository, kode, pengujian atau deployment yang diverifikasi. Keputusan stack dan kebutuhan dirancang sesuai permintaan; detail operasional belum disetujui. Berikutnya: sepakati keputusan terbuka di DECISIONS; buat repo dan prototipe Auth, role/scope, migrasi dan impor; uji sebelum implementasi pengiriman.

> Catatan: paragraf di atas adalah kondisi awal 27 Oktober 2026, sebelum ada kode. Bagian di bawah ditambahkan berurutan; kondisi kode, pengujian dan risiko terkini ada pada bagian **Uji PostgreSQL, konkurensi, dan data contoh — 27 Oktober 2026**. Belum ada rilis atau deployment produksi apa pun.

Saat pekerjaan berjalan, catat branch, commit, status perubahan, keputusan, perintah & hasil tes, environment, risiko, blocker dan next action. Jangan masukkan rahasia atau data murid asli.

## Pembaruan 27 Oktober 2026
Nama SHB Portal. Kebutuhan baru: bilingual Indonesia/English; tema light/dark; upload/download XLSX, filter dan pembagian akun; komunikasi bulk/kelas/individual/pilihan via inbox/email/WhatsApp, status terpisah. HTML adalah simulasi, belum ada server, login, XLSX, email atau WhatsApp aktif. Preview menyediakan terjemahan navigasi utama saja; penerjemahan seluruh isi masih wajib sebelum rilis. Lihat COMMUNICATION_AND_ACCOUNTS.md dan PROJECT_CONSTITUTION.md.

## Pembaruan rekening dan sibling
Tambahkan rekening sekolah yang dikelola kepala sekolah, VA/reference tujuan dalam impor tagihan, snapshot dan audit, serta satu akun wali untuk beberapa anak terverifikasi. Preview tetap simulasi; belum ada CRUD atau integrasi bank. Makna 'susulan' perlu dikonfirmasi.

## Pembaruan bukti transfer
Wali menyalin VA dan mengunggah foto dengan nominal/tanggal; CRUD bukti yang dibuat dibatasi sebelum verifikasi, setelah verifikasi koreksi melalui admin. Admin, wali kelas berwenang dan kepala sekolah dapat melihat foto/nominal; admin verifikasi. Preview masih simulasi, file hanya dilihat secara lokal di browser dan tidak diunggah; tidak ada perubahan database atau pembayaran.

## Pembaruan RBAC dan bantuan
Matriks lengkap pada RBAC_MATRIX.md; tambahkan peringatan jatuh tempo sesuai peran, serta tombol WhatsApp bantuan tetap di kanan bawah. Nomor WhatsApp admin belum diberikan; preview menampilkan informasi nomor belum diatur. Semua halaman dan alert masih menggunakan data contoh, dan hak akses baru spesifikasi bukan enforcement. Bahasa English preview masih parsial. Perlu konfirmasi jumlah hari sebelum jatuh tempo dan apakah batas berarti tanggal atau nominal.

## Pengaturan admin
Admin mengelola jadwal peringatan, nomor WhatsApp admin dan logo sekolah. Preview pengaturan adalah simulasi, belum menyimpan data atau menerapkan perubahan. Nomor dan jadwal awal belum ditentukan.

## Tema warna sekolah
Pengguna menyetujui warna biru tua, merah, hijau dan abu-abu berdasarkan foto sebagai tema SHB Portal. Preview memperbarui palet; kode warna masih pendekatan, belum diuji sebagai standar identitas resmi maupun diuji kontras secara menyeluruh.

## Fondasi kode awal
Fungsi domain murni dan unit test ditambahkan; belum terhubung backend/database. Implementasi role dan scope masih ilustrasi awal, wajib diperluas sesuai assignment sekolah dan diuji di boundary server/database. Preview adalah simulasi. Repository GitHub khusus belum tersedia melalui alat pembuatan repository.

## Django foundation started
Basic Django login/logout, membership and read-only scoped invoice dashboard, initial migration, local tests and optional PostgreSQL TLS settings added. This is not Supabase Auth nor RLS; no Supabase database has been changed. Remaining: isolate project, Supabase Auth and security model, enforce schema invariants, all CRUD/import/export, private receipts, verified payments, notifications, dashboards, full language/theme, and release testing. Do not deploy or use real records.

## Persiapan SQL Supabase
`deploy/supabase_hardening.sql` adalah hardening deny-by-default untuk tabel Django yang sudah dibuat migrasi, bukan migrasi schema atau kebijakan RLS antarperan. `.env.example` dan `docs/SUPABASE_SETUP.md` menjelaskan input aman dan keterbatasan. Tidak ada SQL dijalankan di Supabase; belum diuji Postgres, Supabase Auth maupun RLS end-to-end. Django direct connection perlu otorisasi pada semua operasi, terlepas RLS.

## Akses dashboard lima peran
Dashboard read-only menerapkan scope admin sekolah, orang tua terhubung dan wali kelas ditugaskan; kepala sekolah/yayasan melihat agregat sesuai sekolah. Kondisi sekolah pada kelas dan murid harus sama. Tes SQLite 11 Django dan 5 domain lulus. Ini belum melengkapi RBAC seluruh fitur: CRUD, bukti privat, role assignment, admin bank, email, Supabase Auth dan RLS belum dibuat atau diuji. Jangan gunakan data nyata.

## Tampilan responsif dan aset lokal
Template Django menggunakan CSS dan JavaScript lokal, layout responsif, tema terang/gelap dengan preferensi lokal, dan tabel dapat digeser pada layar kecil. Django tests 12 lulus, aset ditemukan dengan findstatic; belum ada uji visual pada perangkat atau browser nyata. Deployment wajib melayani STATIC_ROOT setelah collectstatic. CSS ini belum Tailwind dan baru mencakup halaman Django yang sudah ada; fitur desain preview belum seluruhnya dibangun.

## Preview XLSX
Admin aktif dapat mengunduh template dan melakukan validasi awal XLSX tanpa menyimpan tagihan. Batas 2 MB, 2.000 baris, ekspansi ZIP 10 MB; formula dan nominal tidak valid ditolak. Belum ada pencocokan murid/kelas/tahun/VA, validasi email dan tanggal lengkap, pemilihan sekolah admin, deduplikasi, commit atau email; jangan gunakan data nyata. Django 15 tes lokal lulus.

## Bukti transfer awal
Django menyediakan unggah foto JPG/PNG, nominal dan tanggal oleh wali yang terhubung; preview private melalui pemeriksaan scope untuk pembuat, admin, kepala sekolah, dan wali kelas; verifikasi hanya admin sesuai sekolah dengan kunci transaksi dan pencegahan verifikasi ulang. Foto disimpan dalam database sementara; butuh strategi private storage dan batas operasional produksi. Belum ada edit/tarik/tolak, penghapusan metadata gambar, RLS Supabase, audit lengkap, pengujian PostgreSQL/paralel dan produksi. Django 18 tes SQLite lokal lulus. Ini masih belum siap untuk data nyata.

## Super admin
Akun Django is_superuser aktif dapat mengakses semua sekolah untuk dashboard dan bukti yang tersedia, serta Django admin untuk membuat/menonaktifkan sekolah dan membership. Status konfigurasi Supabase/Postgres, SMTP, Midtrans ditampilkan hanya sebagai boolean; pengaturan nilai rahasia melalui UI, MFA, audit akses, impersonasi scoped dan integrasi Midtrans belum dibangun. Ini development-only; tidak siap data nyata.

## Data murid awal
Admin sekolah dan superuser dapat melihat, mencari, menambah, mengubah, menonaktifkan dan ekspor XLSX data murid dalam scope; ekspor menghindari formula injection. 24 tes Django SQLite lulus. Relasi wali, impor murid, audit, pagination, RLS dan fitur CRUD lainnya belum selesai; jangan gunakan data nyata.

## Rekening sekolah awal
Kepala sekolah dan superuser dapat menambah, melihat, mengubah, menonaktifkan dan ekspor rekening sesuai scope. 26 tes Django SQLite lulus. Rekening belum terhubung ke tagihan, belum ada snapshot tujuan, audit, impor dan pengujian PostgreSQL/RLS. Jangan gunakan data nyata.

## Email bilingual
Templat pembayaran profesional ID/EN berbentuk HTML inline dan teks biasa disiapkan. Variabel, domain resmi, bahasa per wali, pengiriman multipart, SMTP dan validasi penerima belum terhubung. Tidak ada email yang dikirim.

## Proteksi produksi dan PDP
Tambahkan profil SHB_ENV=production: wajib secret dan hosts eksplisit, DEBUG off, HTTPS redirect dan secure cookies; pengaturan trust proxy opt-in; HSTS opt-in setelah konfigurasi HTTPS teruji. Dokumen PRIVACY_PDP.md memetakan kebutuhan kebijakan dan kontrol yang belum ada. Jangan klaim kepatuhan atau gunakan data nyata sebelum validasi hukum, staging dan audit teknis.

## Uji PostgreSQL, konkurensi, dan data contoh — 27 Oktober 2026
Branch `freebuff/ac9ad268c61424b55ab6a2ea`, perubahan belum di-commit. Yang berubah: `portal/tests.py`, perintah baru `portal/management/commands/seed_demo.py`, `README.md`, dan dokumen ini. `config/settings.py`, `config/urls.py` dan `portal/views.py` tidak diubah. Semua data uji sintetis; tidak ada data murid nyata.

### Lingkungan
- Python 3.12.3 dengan venv `.venv` dari `requirements.txt`: Django 5.2.18, psycopg 3.2.13, openpyxl 3.1.5, Pillow 12.3.0. Django global 6.1 sengaja tidak dipakai agar sesuai pin proyek.
- Preview lokal memakai SQLite `db.sqlite3` (gitignored), diisi dengan `python manage.py seed_demo`.
- **PostgreSQL 16.2 dijalankan sebagai pengguna biasa**, karena image ini tanpa root (sudo diblokir `no-new-privileges`), tanpa daftar paket apt, dan binari EDB mengembalikan 403: `pip install pgserver` (menyertakan binari PostgreSQL) → `initdb -U shb -E UTF8 --auth=trust -D $HOME/shb-pgdata` → `pg_ctl -D $HOME/shb-pgdata -o "-p 55432 -c listen_addresses=127.0.0.1" -l $HOME/pg.log start`. Data dir 62 MB di luar repo; **lingkungan ini tidak persisten** dan harus dibuat ulang setelah restore.
- `config/settings.py` tidak diubah: tes dijalankan dengan `POSTGRES_HOST=/tmp` (socket Unix) sehingga `OPTIONS={'sslmode': 'require'}` tetap ikut diuji.
- Perintah: PostgreSQL `POSTGRES_HOST=/tmp POSTGRES_PORT=55432 POSTGRES_DB=shb POSTGRES_USER=shb POSTGRES_PASSWORD=<kata-sandi-lokal> .venv/bin/python manage.py test portal`; SQLite tanpa variabel `POSTGRES_*`; domain `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests`.

### Hasil uji
| Perintah | PostgreSQL 16.2 | SQLite |
|---|---|---|
| `manage.py test portal` | 34 lulus | 34 lulus, 2 skip |
| `unittest discover -s tests` | 5 lulus | 5 lulus |

Tiga perubahan yang diuji:
1. **`seed_demo`** — data contoh sintetis idempotent (satu sekolah, tiga akun admin/walikelas/ortu, dua kelas, tiga murid, tiga tagihan, satu rekening) agar preview bisa dibangun ulang setelah restore; hanya menambah bagian yang hilang, menolak berjalan saat `SHB_ENV=production`, dan kata sandinya hanya demo. Tiga tes baru termasuk penolakan produksi dan isolasi scope wali.
2. **Perbaikan tes:** `test_guardian_upload_and_cross_family_privacy` dan `test_invalid_photo_rejected` memakai URL keras `/invoices/1/proof/`. Urutan `serial` PostgreSQL tidak ikut rollback saat transaksi tes dibatalkan, sehingga `pk=1` hanya valid pada SQLite; setelah tes lain membuat tagihan, id tersebut tidak ada dan hasilnya 404. Terbukti dengan menjalankan tes itu sendirian (lulus) dan setelah tes pembuat tagihan (gagal). Perbaikan: simpan `self.invoice` di `setUp` dan pakai `self.invoice.pk`; asersi tidak diubah.
3. **`ConcurrentProofVerificationTests`** (dua tes, hanya PostgreSQL) — TransactionTestCase agar data ter-commit dan terlihat koneksi kedua. (a) Dua POST `/proofs/<id>/verify/` bersamaan dari dua thread dengan `Barrier`, `Client` dan koneksi terpisah; menuntut tepat satu 302, satu 400, satu Payment, status VERIFIED dan `reviewed_by` admin. (b) Tes deterministik: satu transaksi memegang lock baris dengan `select_for_update` dan menahan commit; selama itu permintaan verifikasi kedua harus tertahan, lalu setelah commit melihat status VERIFIED dan ditolak 400, dengan tepat satu Payment. Bukti keduanya tidak hampa: saat `select_for_update()` dihapus sementara, keduanya gagal ([302,302] dan verifikasi kedua 302). Catatan penting yang terungkap: tanpa lock, verifikasi kedua tetap tertahan pada `UPDATE` tetapi tetap lolos, karena pemeriksaan status sudah dilakukan sebelum menunggu — itulah race yang dicegah. `portal/views.py` dipulihkan identik dengan HEAD. Pada SQLite keduanya di-skip dengan alasan tercatat (`SELECT ... FOR UPDATE` diabaikan).

### Risiko dan keterbatasan yang tersisa
- **TLS TCP belum teruji.** Binari PostgreSQL ini dikompilasi tanpa SSL (`SSL is not supported by this build`), dan pada socket Unix tidak ada TLS yang dinegosiasikan, sehingga jalur produksi Supabase dengan `sslmode=require` over TCP masih belum diverifikasi.
- **Konkurensi baru diuji dengan dua penulis.** Urutan menunggu lock dan single-payment sudah dibuktikan deterministik, tetapi lebih dari dua penulis paralel, jalur penolakan bukti saat bersamaan, serta deadlock/timeout kunci belum diuji.
- **RLS dan migrasi Supabase belum diuji**, termasuk `deploy/supabase_hardening.sql`. Pemeriksaan akses yang terbukti baru pada tingkat aplikasi Django.
- **Versi mesin berbeda:** pengujian memakai PostgreSQL 16.2; Supabase dapat memakai major version lain sehingga perilaku spesifik versi masih perlu dikonfirmasi.
- **Skip pada SQLite** untuk tes konkurensi bukan bukti lulus; invarian itu hanya terbukti pada PostgreSQL.
- **Lingkungan pengujian tidak persisten** dan perubahan belum di-commit, jadi hasil ini tidak dapat diulang tanpa menjalankan ulang langkah di atas.

Berikutnya: pindahkan pengujian ke instance PostgreSQL/Supabase terisolasi dengan TLS nyata, tambah pengujian konkurensi di atas dua penulis, dan pertimbangkan opsi reset terkontrol pada `seed_demo`.

## Merge origin/main dan penyatuan seed_demo — 27 Oktober 2026
Branch `freebuff/ac9ad268c61424b55ab6a2ea`. Pekerjaan lokal di-commit lebih dulu (`7a796e6`, identitas repo lokal `Codebuff Agent <noreply@codebuff.com>`), lalu main (`deb52f5`) di-merge. `git pull` polos tidak bisa dipakai: branch ini tanpa upstream, dan perubahan lokal menutupi `README.md`, `portal/tests.py` serta `portal/management/`. Konflik hanya pada `seed_demo.py` (add/add) dan `portal/tests.py`; `config/settings.py`, `.env.example`, `README.md`, `home.html` dan `app.css` merge otomatis.

Keputusan penyatuan: satu perintah `seed_demo` yang membuat enam akun demo bawaan main (`superadmin@`, `admin@`, `kepala@`, `yayasan@`, `walikelas@`, `ortu@shb.sch.id`, password `DemoSHB!2026`, tidak menimpa akun atau password yang sudah ada) ditambah data contoh murid, kelas, enrollment, tagihan dan rekening milik branch ini. Guard main dipertahankan: perintah menolak berjalan bila `SHB_ENV=production` atau database bukan SQLite. Nama sekolah memakai `Sekolah Harapan Bangsa (contoh)` agar database pengembangan yang sudah ada dipakai ulang tanpa duplikasi sekolah; main memakai `(Demo)` dan tidak ada tes yang bergantung pada nama itu. Bagian README "Akun demo lokal" diperbarui karena perintah sekarang juga mengisi data murid.

Hasil uji setelah merge: 36 tes Django lulus pada SQLite (2 skip: tes konkurensi) dan pada PostgreSQL 16.2 (4 skip: empat tes seed karena guard SQLite-only), serta 5 tes domain lulus. `migrate` tidak menerapkan migrasi baru dan `seed_demo` idempoten pada database lama (hanya menambahkan enam akun).

Risiko: (1) tes seed kini tidak berjalan pada PostgreSQL karena guard SQLite-only, jadi regresi perintah hanya tertangkap pada SQLite; (2) database pengembangan lama menyisakan tiga akun lama `admin`/`walikelas`/`ortu` yang tidak lagi dibuat perintah ini; (3) guard memakai `settings.DATABASES['default']['ENGINE']`, perlu ditinjau bila engine berubah. Berikutnya: opsi bersih-bersih data contoh lama dan uji pada Supabase terisolasi.

## Korespondensi awal
Admin dapat mengirim pesan individual kepada wali dengan membership aktif pada sekolahnya; pesan tersimpan dalam inbox wali dan SMTP opsional mencatat status accepted/failed. Email default dinonaktifkan, konfigurasi SMTP via environment; tidak ada retry otomatis untuk kegagalan ambigu. 29 tes Django SQLite lulus termasuk outbox simulasi dan isolasi sekolah. Belum ada preview/konfirmasi kedua, bulk, pembatasan kecepatan, validasi email terverifikasi, antrian, audit, Supabase Auth/RLS, pelindungan operasional dan uji SMTP nyata. Belum siap data asli.

## Tarik main terbaru dan verifikasi CSRF preview — 27 Oktober 2026
Main ditarik lagi: satu commit baru `5b943e8` (Test demo role logins with CSRF enforcement) di-merge ke branch ini sebagai `37b6611`; konflik hanya pada `portal/tests.py` dan diselesaikan dengan menjaga kedua sisi. Tes baru itu memanggil `seed_demo`, jadi guard pemeriksaan SQLite yang sama ditambahkan agar tidak gagal pada PostgreSQL. Hasil: 37 tes Django lulus pada SQLite (2 skip) dan pada PostgreSQL 16.2 (5 skip), 5 tes domain lulus; `migrate` tanpa migrasi baru.

Preview dijalankan ulang pada port 3000 dengan `DJANGO_DEBUG=1`, `DJANGO_ALLOWED_HOSTS` memuat host preview, dan `DJANGO_CSRF_TRUSTED_ORIGINS` diisi `https://pv-ac9ad268c614-51b1306d-b202-4d34-b04b-346824493b23.style.dev`. `settings.CSRF_TRUSTED_ORIGINS` pada proses itu sudah memuat origin tersebut (sekali dari environment dan sekali dari penambahan otomatis non-produksi di `config/settings.py`, jadi ada duplikat yang tidak berbahaya). CSRF tidak dinonaktifkan: `CsrfViewMiddleware` aktif, login dengan `Origin` preview berhasil (302 lalu dashboard 200 untuk `ortu@shb.sch.id`), dan login dengan `Origin: https://evil.example.test` ditolak 403.

Blocker: URL HTTPS publik masih mengembalikan 403 berbadan "Preview unavailable. Ask the agent to show the dev server again." dengan header gateway (`server: cloudflare`, `x-frame-options: SAMEORIGIN`) sehingga jelas bukan respons Django (proyek ini mengirim `X-Frame-Options: DENY`). Server sendiri sehat dan melayani host preview secara lokal (200). Perlu dikonfirmasi di browser pemilik; bila panel menampilkan pesan yang sama, coba tampilkan ulang dev server atau buka panel Browser lagi.

## Uji PostgreSQL yang dapat diulang — 27 Oktober 2026
`scripts/pg_test.sh` menyiapkan cluster PostgreSQL sebagai pengguna biasa (pgserver, socket Unix karena binari itu tanpa SSL dan `sslmode=require` hanya bisa lewat socket), menjalankan `manage.py test portal`, lalu mematikan cluster yang ia nyalakan; `KEEP_RUNNING=1` menyisakannya hidup dan `SHB_PGDATA`/`SHB_PGPORT` memisahkan cluster. Skrip membuat `.venv` dan memasang `requirements.txt` sendiri bila worktree baru di-restore, sehingga satu perintah cukup untuk mengulang pengujian. `docs/POSTGRES_TESTING.md` memuat prasyarat, hasil yang diharapkan (SQLite 2 skip, PostgreSQL 5 skip), cara membersihkan, batasan (versi mesin, tanpa TLS/RLS, bukan pengganti staging) dan penanganan masalah. Pengaturan proyek tidak diubah.

## Preview chunked POST dan CSRF 403 — 27 Oktober 2026
Gejala: mencoba login lewat URL preview mengembalikan halaman Django `403 CSRF verification failed — Reason given for failure: CSRF token missing`, padahal form login memuat `{% csrf_token %}`, cookie `csrftoken` ikut terkirim, dan origin preview sudah ada di `CSRF_TRUSTED_ORIGINS`.

Bukti dari log `runserver` (`/tmp/shb-server.log`), bukan dugaan: POST pemilik pada 11:53:47 dicatat `Forbidden (CSRF token missing.)` lalu `"POST /accounts/login/ HTTP/1.1" 403 2491`, dan pada detik yang sama `code 400, message Bad request syntax ('88')` beserta `"88" 400 -`. `0x88` = 136 byte, yaitu ukuran badan form login yang terisi; baris `88` adalah ukuran chunk, bukan permintaan. Kesimpulan: proxy preview mengirim ulang badan POST dengan `Transfer-Encoding: chunked`, sedangkan **server WSGI bawaan `runserver` (wsgiref) tidak mendekode badan chunked**, sehingga `request.POST` kosong dan Django melaporkan token "missing" — cookie ada dan pemeriksaan origin lolos, jadi ini transport, bukan konfigurasi CSRF.

Reproduksi terkendali di dalam VM memakai cookie, token dan `Origin` yang sama: POST dengan `Content-Length` → `302` ke `/dashboard/`; POST identik dengan `-H 'Transfer-Encoding: chunked'` → `403` berukuran 2491 byte dengan halaman yang sama persis, dan log mencatat `Bad request syntax ('83')` (131 byte = ukuran badan uji). Audit 11 form POST pada 17 template: semua menaruh `{% csrf_token %}` di dalam `<form>`; tidak ada form yang kurang token. `CsrfViewMiddleware` tetap aktif dan tidak ada pengaturan CSRF yang dilonggarkan.

Perbaikan: `.venv/bin/pip install daphne` (terpasang 4.2.3; **tidak** ditambahkan ke `requirements.txt` karena hanya untuk server pengembangan) dan `config/settings.py` menyisipkan `daphne` ke awal `INSTALLED_APPS` **hanya bila paketnya bisa diimpor**, sehingga `manage.py runserver` menjadi ASGI dan mendekode badan chunked. Bila daphne tidak ada, jalur WSGI lama tetap berjalan tanpa error. Satu temuan tambahan saat menguji: daphne mewajibkan `ASGI_APPLICATION`, dan tanpa itu `runserver` langsung berhenti dengan `CommandError: You have not set ASGI_APPLICATION`; `ASGI_APPLICATION = 'config.asgi.application'` ditambahkan (entrypoint `config/asgi.py` sudah ada sejak awal, tidak ada file baru).

Hasil uji setelah perbaikan (pid 29020, mendengarkan `0.0.0.0:3000`): POST dengan `Transfer-Encoding: chunked` ke `/accounts/login/` → `302` — kasus yang sebelumnya 403 — dengan badan uji 136 byte sehingga baris chunk-nya `88`, yaitu tanda yang sama persis dengan kegagalan pemilik; POST `Content-Length` → `302`; `/` dan `/static/portal/app.css` → `200` melalui host preview; login `ortu@shb.sch.id` lalu `/dashboard/` → `200` menampilkan hanya `Murid Contoh 1` dan `Murid Contoh 2`; login `walikelas@shb.sch.id` lewat POST chunked lalu `/dashboard/` → `200`; log tidak lagi memuat `Bad request syntax` (0 baris) dan mencatat format ASGI. CSRF tidak dilonggarkan: POST dengan `Origin: https://evil.example.test` tetap `403` dengan alasan `Origin checking failed`. `manage.py test portal` 37 lulus (2 skip) pada SQLite dan 5 tes domain lulus. Guard fallback diuji dengan memaksa `import daphne` gagal: `'daphne' in settings.INSTALLED_APPS` bernilai `False` dan aplikasi tetap siap.

Bukti mentah log WSGI sebelum perbaikan disimpan sementara di `/tmp/shb-server-wsgi-before-fix.log` (di luar repo, hilang setelah restore); baris pentingnya dikutip di atas.

Risiko dan batasan: (1) perbaikan ini hanya menyangkut cara preview lokal dijalankan; tidak ada bukti apa pun tentang produksi. (2) Karena `requirements.txt` sengaja tidak memuat daphne, setelah restore agent harus memasang daphne lagi, jika tidak semua POST di preview akan kembali 403 tanpa memengaruhi aplikasi; `ASGI_APPLICATION` aman dibiarkan ada karena hanya dibaca oleh server ASGI. (3) `runserver` (ASGI maupun WSGI) bukan server produksi; deployment harus memakai server sungguhan di belakang proxy yang menangani `Transfer-Encoding: chunked`. (4) URL HTTPS publik masih mengembalikan 403 milik gateway preview seperti dicatat di bagian sebelumnya, jadi pengujian di browser pemilik masih menunggu. (5) Bila perilaku proxy preview berubah, temuan ini perlu ditinjau ulang; gejalanya bisa dibedakan lewat baris `Bad request syntax` pada log.


## CI: suite pada SQLite dan PostgreSQL — 27 Oktober 2026
Ditambahkan `.github/workflows/tests.yml`, satu-satunya berkas CI; sebelumnya direktori `.github/` belum ada. Menjalankan dua job pada `ubuntu-latest` dengan Python 3.12 (sama dengan venv yang dipakai pengujian lokal):

- **`sqlite`** — memasang `requirements.txt` lalu menjalankan `python manage.py test portal` (37 tes, 2 skip: tes konkurensi).
- **`postgresql`** — menjalankan `./scripts/pg_test.sh` dengan `SHB_PGDATA=${{ runner.temp }}/shb-pgdata` dan `SHB_PGPORT=55432`. Skrip itu sendiri yang membuat `.venv`, memasang `requirements.txt` dan `pgserver` (binari PostgreSQL tanpa root, sudo atau paket apt), `initdb`, menyalakan cluster pada socket Unix, menjalankan suite (37 tes, 5 skip: tes seed yang SQLite-only), lalu mematikan cluster yang ia nyalakan. Skrip keluar dengan status test runner, sehingga tes gagal menggagalkan step. Log cluster diunggah sebagai artifact hanya saat terjadi kegagalan.

Kedua job diperlukan: tes konkurensi hanya berjalan di PostgreSQL dan tes seed hanya di SQLite, jadi hijau di satu mesin bukan bukti untuk mesin lain. Trigger: push ke `main`, pull request, dan `workflow_dispatch`; `permissions: contents: read`; concurrency membatalkan run lama pada ref yang sama.

Verifikasi yang bisa dilakukan tanpa runner GitHub: YAML di-parse dan strukturnya diasertikan (hanya job `sqlite` dan `postgresql`, perintah yang diharapkan ada, setiap step punya `uses` atau `run`); `scripts/pg_test.sh` bermode 755 sehingga `./scripts/pg_test.sh` dapat dipanggil pada checkout bersih; simulasi job PostgreSQL dari direktori data kosong (`SHB_PGDATA=/tmp/ci-sim-pgdata SHB_PGPORT=55433`) berhasil `initdb` → 37 tes lulus → 5 skip → cluster dimatikan → exit 0; perintah job SQLite exit 0. **Belum dijalankan pada runner GitHub sungguhan**, jadi perilaku runner (image, cache pip, ketersediaan wheel `pgserver` untuk platform tersebut) belum terbukti dari sini.

Risiko: `actions/checkout`, `actions/setup-python` dan `actions/upload-artifact` dipin ke tag major (`@v4`/`@v5`), bukan ke SHA commit. Belum ada lint, `collectstatic` maupun unggahan coverage, dan tidak ada job khusus untuk 5 tes domain. `pyyaml` dipasang hanya di venv lokal untuk memvalidasi YAML dan tidak ditambahkan ke `requirements.txt`; data uji simulasi di `/tmp` sudah dihapus.

## URL preview publik 403 padahal origin 200 — 27 Oktober 2026
Gejala: `https://pv-ac9ad268c614-51b1306d-b202-4d34-b04b-346824493b23.style.dev/` — dan setiap path lain — mengembalikan `403` berbadan 64 byte "Preview unavailable. Ask the agent to show the dev server again.", sementara origin lokal (pid 29020, `0.0.0.0:3000`) menjawab `200` untuk Host yang sama.

Bukti yang dikumpulkan:

- Hostname mengarah ke Cloudflare (`208.72.218.28`, `2602:f470:1::28`), TLS 1.3 dengan sertifikat `*.style.dev`. Respons membawa `server: cloudflare`, `x-render-origin-server: Render`, `rndr-id`, dan `vary: rsc, next-router-state-tree…`, jadi gateway-nya aplikasi Next.js di Render — bukan Django (proyek ini mengirim `X-Frame-Options: DENY`, gateway `SAMEORIGIN`).
- Path yang **tidak ada** di aplikasi (`/definitely-not-a-route-xyz`) menerima status dan badan yang sama persis, jadi penolakan terjadi sebelum perutean per-path dan tidak berasal dari aplikasi.
- Permintaan bergaya browser lengkap (User-Agent Chrome, `Origin`, `Referer`, `Accept`, `Accept-Language`, `Sec-Fetch-*`) juga ditolak 403, jadi header bukan penyebabnya.
- Selama 12 probing ke URL publik — dua di antaranya tepat setelah `cloud_show_dev_server` mengembalikan `ready: true` — log origin tidak bertambah satu baris pun (`delta=0`): **gateway tidak pernah menghubungi VM ini**. Maka port 3000, binding `0.0.0.0`, `ALLOWED_HOSTS`, firewall, CSRF dan kode aplikasi tidak terlibat sama sekali.
- Perilaku ini konsisten dengan rute yang kedaluwarsa ketika runner diganti di tengah turn sebelumnya: pada 11:52–11:56 browser pemilik sempat mencapai Django lewat rute itu (log origin mencatat GET login + aset statis + POST, termasuk 403 CSRF chunked), lalu berhenti tepat setelah runner restart.
- Tidak ada proses tunnel/proxy di dalam VM (hanya `runserver`, `sshd`, `dockerd`, `freestyle-vms-agent`), jadi tidak ada yang bisa diperbaiki dari sisi VM.
- **Jalur viewer platform tetap berfungsi.** Setiap kali `cloud_show_dev_server(3000)` dipanggil, log origin mencatat probe dari `127.0.0.1` **lalu** pengambilan halaman dari `10.31.252.165` — alamat privat di luar VM ini (alamat VM: `169.254.77.2` pada `eth0`, `172.17.0.1` pada `docker0`) — yang memuat `/` beserta `/static/portal/app.js` dan `/static/portal/app.css` dengan status 200/304. Itu pola klien yang benar-benar merender halaman, dan terjadi tiga kali berturut-turut setelah pendaftaran ulang. Jadi dev server memang disajikan ke panel; yang gagal adalah hostname publik `pv-*.style.dev` untuk permintaan yang tidak membawa sesi klien.
- VM juga melayani klien non-loopback: `GET /` lewat `169.254.77.2:3000` dengan Host preview → `200`, jadi binding dan perutean jaringan VM bukan penyebabnya.

Batasan penting: pengujian ini dijalankan dari dalam VM **tanpa cookie sesi klien**, sehingga tidak bisa membedakan "rute publik memang kedaluwarsa" dari "permintaan tanpa sesi klien ditolak oleh edge publik". Bukti viewer (di atas) menunjukkan yang bermasalah adalah hostname publik, bukan aplikasi maupun dev server. Yang bisa dipastikan hanyalah bahwa gateway tidak meneruskan permintaan tersebut ke origin. Karena itu verifikasi akhir harus dilakukan di browser pemilik setelah panel Browser dimuat ulang; bila masih 403, urutannya adalah muat ulang panel lebih dulu, lalu minta agen menampilkan dev server lagi. Managed deployer Sites tidak menjalankan server Python/Django, jadi tidak ada jalur publik lain di platform ini selain preview dev server; alternatifnya menjalankan aplikasi di komputer pemilik. Aplikasi sendiri tetap terbukti sehat: 37 tes lulus di SQLite dan PostgreSQL, login ber-CSRF terverifikasi lokal, dan perbaikan POST chunked sudah terpasang.