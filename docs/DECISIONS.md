# Keputusan dan pertanyaan terbuka

Sudah diminta: kelas dan lima role, XLSX, Python, Tailwind, Supabase, Gmail SMTP, pengumuman, dashboard, lifecycle murid dan akun. Rekomendasi awal: Django, Supabase Auth + Postgres, Redis/worker, pencatatan pembayaran manual terverifikasi; perlu validasi teknis dan persetujuan.

1. Apakah sistem hanya memberi tahu, atau juga menerima dan merekonsiliasi pembayaran? Metode pembayaran, rekening resmi, bukti dan PIC?
2. Siapa boleh melihat rincian individu? Cakupan wali kelas, kepala sekolah dan yayasan? Satu atau beberapa sekolah?
3. Berapa murid, wali dan email per hari? Apakah Gmail mencukupi kuota dan kebijakan akun? Bila tidak, pilih SMTP transaksional.
4. NIS/NISN wajib yang mana, aturan keunikan, email wali lebih dari satu dan verifikasi hubungan bagaimana?
5. Definisi jenis/periode tagihan, tenggat, denda, cicilan, pembayaran lebih, pembatalan, koreksi dan mekanisme persetujuan?
6. Jadwal pengingat, kanal, preferensi privasi isi email, kontak dan domain resmi?
7. Aturan naik kelas, tinggal kelas, pindah, 9 ke 10, lulus, alumni, masa retensi dan arti reset?
8. Hosting/domain, biaya, backup, target pemulihan, MFA staf, penanggung jawab data dan persetujuan yang diperlukan?
9. Kelas 11 dan 12 tanpa paralel sesuai input; apakah akan ada kelas tambahan atau jurusan?

## Pembaruan SHB Portal
Diputuskan: 1–3 wali per murid; akun dibagikan lewat undangan aktivasi; opsi pengiriman portal/email/WhatsApp, bulk/kelas/individu/custom; UI bilingual dan light/dark. Belum diputuskan: model persetujuan WhatsApp, penyedia/biaya, bahasa email pilihan per wali, format spreadsheet multiwali dan kebijakan rincian individual bagi wali kelas. Tetapkan sebelum implementasi produksi.

## Keputusan rekening dan sibling
Diminta: kepala sekolah CRUD rekening sekolah; XLSX memuat VA atau tujuan transfer bank; satu akun wali untuk beberapa anak. Perlu klarifikasi arti 'susulan ke alamat bank tertentu': apakah instruksi transfer, rekening alternatif, atau VA menyusul setelah impor. Juga tentukan siapa berwenang mengoreksi tujuan pada tagihan yang sudah terbit, apakah nomor VA diberikan bank dan apakah pembayaran otomatis direkonsiliasi.
