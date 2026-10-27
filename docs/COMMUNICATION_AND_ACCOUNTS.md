# SHB Portal — komunikasi dan akun

## Admin: alur pengiriman
1. Pilih semua wali, kelas tertentu, satu wali, atau beberapa wali; filter berdasarkan tahun, jenjang, kelas, jenis tagihan dan status relevan.
2. Pilih pesan portal, email pribadi dan/atau WhatsApp. Akun wali menerima pesan portal ketika kanal itu dipilih; email/WhatsApp dikirim ke kontak wali yang terverifikasi dan memenuhi persetujuan/kebijakan. Satu murid dapat punya 1–3 wali, satu wali dapat punya beberapa anak.
3. Isi subjek dan isi custom atau templat dengan variabel aman. Simulasikan personalisasi per wali dan anak; jangan menggabungkan data anak lintas keluarga. Pastikan setiap wali hanya menerima detail murid yang berhak ia lihat.
4. Preview jumlah wali, jumlah pesan dan kanal, kontak bermasalah, duplikasi, biaya yang mungkin berlaku dan waktu pengiriman. Minta konfirmasi admin sebelum submit. Simpan audit dan kunci idempotensi.
5. Pantau setiap penerima × kanal: pending, accepted/sent, gagal; delivered/read hanya bila provider benar-benar melaporkannya. Retry kegagalan dengan aturan aman; kegagalan satu kanal tidak membatalkan kanal lain. Status bayar independen.

## Akun
Upload data wali dari XLSX atau tambah manual. Admin dapat memfilter, memilih dan mengirim ulang undangan individual. Tidak pernah ekspor password/token. Aktivasi via link Auth satu kali; reset via Auth dengan respons generik, expiry dan pembatasan permintaan. Perubahan email perlu verifikasi ulang. Menu wali: inbox, tagihan per anak, riwayat pembayaran, pengumuman, profil dan logout.

## Integrasi
Rancangan provider: Gmail SMTP untuk email, Supabase Auth untuk email autentikasi, WhatsApp Business Platform untuk pesan otomatis resmi. Tentukan apakah SMTP Auth dan aplikasi perlu konfigurasi masing-masing. Pengiriman WhatsApp memerlukan akun/nomor, consent, template yang disetujui bila diwajibkan, integrasi webhook status dan anggaran; jangan menganggap WhatsApp biasa sebagai API massal otomatis. Jangan mengirim ke penerima nyata pada preview/staging.
