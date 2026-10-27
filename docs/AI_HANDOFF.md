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
