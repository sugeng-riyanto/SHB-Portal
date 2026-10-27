# Syarat rilis

- Persetujuan pemilik sekolah atas aturan keuangan, peran, cakupan dan komunikasi.
- CI lulus untuk commit rilis, termasuk tes lintas role, RLS/bypass backend, import idempotent, pembayaran dan tahun ajaran; jelaskan skip dan buktikan tes kritis berjalan.
- Staging dengan data sintetis: aktivasi/reset, undangan, akses wali, impor, pembayaran dan email ke alamat uji berhasil.
- Pemetaan wali dan alamat diverifikasi; preview sasaran; pengiriman massal hanya dengan persetujuan dan kontrol bertahap.
- Backup dan latihan restore berhasil; migrasi dan rollback diperiksa. Secrets, HTTPS, rate limit, audit dan monitoring aktif.
- Kelayakan SMTP dan kuota diverifikasi, ada penanganan gagal; tidak menyatakan email berhasil sampai ada bukti.
- Dashboard mobile dan aksesibilitas diuji. Dokumen operasi, PIC dan prosedur insiden tersedia. Tidak ada blocker keamanan terbuka.
