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

## Alur perubahan tabel dan database (diputuskan 27 Oktober 2026)
Diputuskan: **migration Django adalah satu-satunya sumber utama perubahan skema.** Tabel yang sama tidak dibuat ulang melalui Dashboard Supabase atau migration Supabase, dan tidak ada antarmuka (termasuk dashboard integrasi) yang menjalankan SQL bebas dari browser.

Alur kerja yang disetujui:

1. Permintaan perubahan disampaikan lewat chat, tanpa menulis SQL sendiri.
2. Perubahan disiapkan sebagai migration Django di repositori, beserta tes hak akses dan data sintetis.
3. Migration dijalankan lebih dulu pada Supabase **staging**, lalu hasilnya diperiksa (inventaris tabel, status RLS dan akses Data API, isolasi peran).
4. Setelah pemeriksaan lolos dan backup tersedia, perubahan diterapkan ke produksi dan dicatat di `AI_HANDOFF.md`.

Pengamanan yang menyertainya: kredensial database hanya di server/secret manager, bukan di browser, Git, atau chat; otorisasi tetap ditegakkan di backend walaupun koneksi melewati RLS; tabel hanya diekspos ke Data API bila RLS dan grant minimal sudah tersedia; staging terpisah dan uji restore wajib sebelum data murid nyata (lihat `BACKUP_RESTORE.md`, `SUPABASE_SETUP.md`, `RELEASE_GATES.md`).

Status: belum ada perubahan yang dijalankan. Proyek staging `uxmdorvxnzelpduvkpuj` masih tanpa tabel, dan kredensialnya belum tersedia di workspace ini.

## Kunci enkripsi integrasi (diputuskan 27 Oktober 2026)
Diputuskan: `SHB_INTEGRATION_ENCRYPTION_KEY` disimpan di server/secret manager — bukan di browser, Git, atau chat — dan nilainya tidak pernah ditampilkan kembali. Kunci **tidak boleh digenerate ulang** selama masih ada baris `IntegrationConfig` terenkripsi, karena data lama tidak dapat didekripsi lagi; penggantian kunci harus berupa prosedur dekripsi-ulang yang dicatat. Backup terbatas disimpan terpisah dari aplikasi dan juga di password manager sekolah.

Status: kunci dibuat 27 Oktober 2026 (sidik jari SHA-256 16 hex `a63b4109d0b67d45`), disimpan di `.secrets/` yang diabaikan Git, dan diberikan ke preview melalui environment proses.
