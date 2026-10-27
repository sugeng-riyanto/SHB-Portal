# Arsitektur usulan

Browser responsif → Django HTTPS (UI, validasi, otorisasi dan API) → database Postgres Supabase. Supabase Auth menangani identitas; backend memverifikasi token melalui mekanisme resmi dan memeriksa peran/lingkup pada setiap request. Worker dan scheduler mengambil notifikasi dari antrean/outbox; SMTP Gmail mengirim email individual. Redis adalah kandidat broker, tetapi pilihan final ditentukan berdasarkan hosting dan anggaran.

Database menyimpan data sebagai sumber kebenaran, bukan spreadsheet. Gunakan transaksi untuk commit impor dan outbox; worker mengirim di luar transaksi. Jangan mengekspos kredensial server ke browser. Jika Data API diaktifkan, tabel yang terekspos wajib RLS dan grants minimal; layanan berprivilege yang melewati RLS tetap wajib validasi otorisasi pada backend. Tentukan satu alur Auth untuk aktivasi/reset (Supabase Auth) dan konfigurasikan SMTP serta redirect yang diizinkan; aplikasi tidak membuat token sandi paralel. Pastikan email dari Auth dan email aplikasi memiliki pengaturan SMTP terpisah jika diperlukan.

Pisahkan development, staging dan produksi; gunakan data sintetis. Simpan waktu dalam UTC dan tampilkan Asia/Jakarta. Gunakan migrasi versi, indeks sesuai pola query, paginasi, agregasi di server dan monitoring kuota Supabase. MVP tanpa integrasi bank atau payment gateway.
