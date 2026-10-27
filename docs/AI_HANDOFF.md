# Serah terima agen

Tanggal: 27 Oktober 2026. Status: spesifikasi awal saja; tidak ada repository, kode, pengujian atau deployment yang diverifikasi. Keputusan stack dan kebutuhan dirancang sesuai permintaan; detail operasional belum disetujui. Berikutnya: sepakati keputusan terbuka di DECISIONS; buat repo dan prototipe Auth, role/scope, migrasi dan impor; uji sebelum implementasi pengiriman.

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

## Korespondensi awal
Admin dapat mengirim pesan individual kepada wali dengan membership aktif pada sekolahnya; pesan tersimpan dalam inbox wali dan SMTP opsional mencatat status accepted/failed. Email default dinonaktifkan, konfigurasi SMTP via environment; tidak ada retry otomatis untuk kegagalan ambigu. 29 tes Django SQLite lulus termasuk outbox simulasi dan isolasi sekolah. Belum ada preview/konfirmasi kedua, bulk, pembatasan kecepatan, validasi email terverifikasi, antrian, audit, Supabase Auth/RLS, pelindungan operasional dan uji SMTP nyata. Belum siap data asli.

## Penegasan alur bulk
User menegaskan prioritas upload XLSX → pilih semua/kelas/grup/individu → kirim massal. `portal/recipients.py` menyiapkan seleksi wali per kelas berbasis sekolah/kelas dengan deduplikasi akun; uji lintas sekolah lulus. Fungsi belum terhubung UI atau pengiriman, tidak memproses per-tagihan dan tidak mengirim email. Fitur bulk, grup, commit XLSX dan queue belum selesai.

## Profil dan password awal
Login Django membuat profil awal yang mewajibkan perubahan password sebelum masuk dashboard; halaman profil mendukung nama dan foto JPG/PNG tervalidasi, foto hanya dapat dibuka pemilik. Toggle lihat password memakai JS lokal. 36 tes SQLite lulus. Belum terintegrasi Supabase Auth, enkripsi foto di storage privat, audit, rate limit atau pengujian produksi. Akun yang dibuat di luar alur login perlu diuji pada integrasi selanjutnya.

## Landing page dan kabar sekolah
Landing page menggunakan bahasa yang lebih hangat; halaman /kabar-sekolah/ menampilkan maksimal enam kabar yang telah diterbitkan dan waktu publikasinya sudah tiba. Superuser Django dapat mengelola SchoolUpdate di /admin/; belum ada antarmuka admin sekolah. Link Instagram/Facebook/YouTube diatur melalui environment HTTPS dan dibuka pada tab baru. Belum ada akun resmi yang dikonfigurasi. Dua tes lokal lulus; belum ada uji visual browser.

## Bahasa
Default English dan pilihan English/Indonesia/Mandarin Tradisional pada bagian landing, navigasi, login dan dashboard dasar. Terjemahan masih parsial: formulir Django, teks dinamis, pengumuman, email, beberapa halaman fitur, tombol tema dan pesan validasi belum seluruhnya diterjemahkan; jangan klaim bilingual lengkap. CSS/JS tetap lokal.

## Bukti transfer: edit dan tarik
Wali pemilik dengan relasi aktif dapat mengubah nominal/tanggal/foto dan menarik bukti pending. Bukti diverifikasi tidak dapat diubah/ditarik; uji pemilik dan wali lain lulus di SQLite. Riwayat perubahan field/audit, validasi konkurensi PostgreSQL, storage terenkripsi, seluruh RBAC/CRUD dan terjemahan tetap belum lengkap.

## Validasi XLSX tambahan
Preview XLSX kini memeriksa format email, tanggal ISO dan referensi tagihan duplikat di dalam file. Uji khusus lulus; validasi belum memastikan kepemilikan email/kelas/bank, belum melakukan commit tagihan atau pengiriman massal. Pengujian 43 tes Django sebelumnya lulus pada SQLite; tidak membuktikan Supabase, SMTP nyata, maupun seluruh release gates.

## CRUD konfigurasi integrasi super admin
Super admin dapat menyimpan, membaca status, mengubah, dan menghapus konfigurasi Supabase, SMTP, Midtrans. Secret disimpan terenkripsi Fernet dengan SHB_INTEGRATION_ENCRYPTION_KEY dari environment; jika kunci hilang data tidak dapat dibaca dan perlu dimasukkan ulang, sehingga kunci dan backup harus dikelola aman. Secret tidak ditampilkan dalam form. Pengaturan UI ini belum digunakan untuk koneksi SMTP, Supabase Auth, DB atau Midtrans, dan belum ada tes koneksi, audit, MFA, rotasi kunci, uji Postgres/produksi; active adalah status konfigurasi bukan integrasi aktif. Tiga tes terarah lulus lokal. Jangan gunakan kredensial nyata sebelum pengamanan dan staging lengkap.

## Tema super admin dan membuka secret
Halaman Django admin diberi tema SHB menggunakan CSS lokal, bukan Tailwind (instalasi Tailwind tidak tersedia pada lingkungan ini). Menu menuju users, sekolah, peran, integrasi dan portal tetap menggunakan otorisasi Django yang ada. Superuser dapat melihat secret integrasi setelah memasukkan password lagi; response no-store, percobaan dibatasi 5/15 menit oleh Django cache, dan aksi dicatat tanpa nilai secret. Cache default lokal per proses tidak memadai untuk produksi multiworker; MFA, audit tersentral, cache bersama, kebijakan retensi dan uji keamanan masih diperlukan. Pengaturan yang disimpan tetap belum terhubung ke layanan. Tes terarah SQLite 2 lulus; UI browser belum diuji. Jangan masukkan kredensial nyata sebelum staging aman.

## Pemeriksaan bukti dan komentar
Tambah filter kelas, pilihan beberapa bukti, total nominal pada browser, verifikasi massal atomik (maks. 100 per permintaan) dan komentar pribadi pemilik bukti/admin. Pengunggahan diuji dengan CSRF aktif di Django test client. Tiga tes terarah lulus di SQLite; preview Freebuff tidak diakses, penyebab CSRF hilang pada preview belum diketahui. Perlu uji Postgres concurrency, audit, UI browser, admin koreksi nominal dan grup khusus; belum siap data asli.

## Navbar responsif
Navbar portal memakai tombol menu pada viewport kecil, target sentuh lebih besar, layout bahasa dan navigasi menyesuaikan layar, serta fallback tetap tampil saat JS tidak tersedia. Tes render dan pilihan bahasa lulus; belum ada uji visual pada browser/perangkat nyata. Django admin memiliki navbar sendiri.

## Preview bukti 404 dan CSRF
Tautan unggah pada dashboard hanya ditampilkan kepada wali yang benar-benar terhubung, dengan membership aktif; admin dan guru tetap dapat melihat bukti sesuai scope tetapi tidak mendapat tautan unggah. `seed_demo_data` menambahkan murid, kelas dan tagihan contoh hanya untuk SQLite development, tanpa mengubah password. Tests lokal: demo guardian bisa membuka form, guru ditolak, submit CSRF aktif lulus. Preview Freebuff belum diakses; error token missing tetap perlu diagnosis di environment aktual.

## Jenis pembayaran, aktivitas dan visualisasi awal
Admin sekolah/superadmin dapat mengelola PaymentType dan ekspor; default Monthly, ECA, Annual Fee, Stationery dan Late Fee ditambahkan melalui aksi eksplisit per sekolah. Kategori belum terhubung ke invoice/impor. ActivityEvent baru mencatat aksi jenis pembayaran, bukan seluruh aktivitas user. Dashboard menampilkan grafik jumlah tagihan per bulan dalam scope dan ekspor XLSX tagihan sesuai scope. Ekspor bukan bukti pembayaran digital, tidak ditandatangani, dan belum mencakup agregat yayasan/kepala sekolah; spider/radar, timeseries keuangan, bukti digital diverifikasi dan audit lengkap belum selesai. Tes terarah SQLite lulus; Postgres/RLS/browser belum diuji.

## Pemisahan dashboard super admin dan admin sekolah
Dashboard menampilkan judul, menu dan scope berbeda: super admin lintas sekolah; admin sekolah sesuai membership aktif. Ringkasan admin sekarang menghitung hanya invoice dalam lingkup sekolahnya. Grafik ditata ulang untuk lebar layar kecil; dua tes akses/scope lulus lokal. Belum diuji visual pada perangkat nyata atau terhadap Supabase/RLS; semua grafik dan analitik yang direncanakan belum lengkap.

## Bukti lunas awal
Verifikasi bukti oleh admin menerbitkan PaymentReceipt hanya bila pembayaran terverifikasi memenuhi nominal+ denda, dengan nomor acak dan kode enam karakter. User dalam scope dapat unduh PDF dengan QR ke halaman verifikasi admin; admin login dibatasi scope sekolah. Tes parsial/lunas, PDF dan lintas sekolah lulus lokal SQLite. Ini belum tanda tangan digital atau sertifikat anti-pemalsuan offline. Gambar, tombol share WhatsApp/email, scan kamera, pencabutan/penggantian bukti jika koreksi, pembatasan percobaan, log verifikasi dan uji PostgreSQL/concurrency belum ada. QR perlu URL resmi HTTPS/proxy benar. Jangan pakai data nyata atau klaim siap produksi.

## Pengumuman kegiatan dan persetujuan kepala sekolah
Admin sekolah dapat membuat/mengubah/menghapus draft berisi judul, paragraf, tanggal dan tautan PDF HTTPS, lalu kirim untuk persetujuan. Kepala sekolah dengan membership aktif pada sekolah terkait dapat menyetujui; approved immutable; QR menuju halaman verifikasi yang memerlukan login admin/kepala sekolah sesuai scope. QR adalah referensi verifikasi dalam portal, bukan tanda tangan digital tersertifikasi. 2 tes terarah SQLite lulus. Belum ada PDF upload/embed, generator teks AI, penerbitan ke halaman publik/akun wali, notifikasi, pembatalan/revisi pascaapproval, audit lengkap, validasi Postgres concurrency atau e-signature. Jangan gunakan data nyata sebelum staging/security selesai.

## Impor data murid XLSX
Admin/superadmin dapat mengunduh template NIS dan nama murid, unggah, preview validasi, lalu menyimpan seluruh baris valid dengan konfirmasi. Akses dibatasi sekolah, duplikasi dicek, session preview berlaku 20 menit, dan commit atomik. Dua tes SQLite lulus untuk scope, NIS teks, duplikasi dan replay. Template ini belum memasukkan kelas, NISN, wali/email, sehingga bukan impor tagihan dan belum menghubungkan akun wali. Uji PostgreSQL/concurrency, audit dan data nyata belum dilakukan.
