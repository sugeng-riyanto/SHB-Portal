# Model data konseptual

| Entitas | Atribut dan batasan utama |
|---|---|
| school, academic_year | lingkup sekolah; label unik per sekolah; tanggal mulai/akhir, status |
| class | tahun, jenjang, nama; unik dalam tahun dan sekolah |
| student | ID internal UUID, NIS/NISN teks, nama, status; aturan keunikan NIS/NISN disepakati per sekolah |
| enrollment | student, tahun, kelas, status aktif/pindah/lulus; maksimal satu enrollment aktif per tahun |
| profile, role_assignment | auth user, peran, lingkup dan masa berlaku; hak tidak disimpan dalam metadata pengguna yang dapat diedit |
| guardian_student | wali, student, hubungan, status verifikasi dan hak; unik wali-murid |
| teacher_class | guru, kelas, tahun, periode penugasan |
| invoice | student, tahun, jenis, periode, jatuh tempo, status, reference unik, nominal dan denda integer IDR |
| payment | invoice, nominal, tanggal, metode, reference, status verifikasi, pembuat; koreksi melalui transaksi/void terjejak |
| adjustment | invoice, jenis, jumlah, alasan, aktor; aturan dampak saldo disepakati |
| import_batch, import_row | hash/file, aktor, status, validasi dan hasil commit; kebijakan retensi |
| notification, outbox | invoice/event, penerima, template, idempotency key, status, percobaan, next_retry, provider ID |
| announcement, audience | isi, status, jadwal dan target peran/kelas/jenjang |
| audit_event | aktor, aksi, entitas, timestamp dan hasil; batasi akses |

Foreign key, check >= 0, constraint keunikan dan transaksi sesuai kebijakan; jangan gunakan floating point untuk uang. Simpan snapshot nama kelas jika diperlukan untuk dokumen historis, sementara hubungan tahun/kelas tetap terjaga. RLS per relasi dan cakupan, serta indeks foreign key dan filter setelah mengukur query. Hubungan riwayat tidak dihapus saat tahun berubah. Masa retensi dan kebijakan NIS/NISN perlu persetujuan.

## Tambahan rekening dan VA
- `school_bank_account`: id, sekolah, bank, nama_pemilik, nomor_rekening teks, status, keterangan dan audit; kepala sekolah kelola sesuai scope. Referensi historis dilindungi; nonaktif menggantikan hapus bila telah digunakan.
- `invoice_payment_destination`: invoice, referensi rekening, snapshot bank/nama pemilik/nomor rekening, nomor_va teks opsional, petunjuk transfer dan versi/waktu penerbitan. Koreksi eksplisit dan audit, hindari ekspos VA di log.
- `guardian_student`: satu profil wali dapat memiliki beberapa relasi murid dan tiap murid 1–3 wali, validasi identitas dan hubungan sebelum mengaitkan. Status relasi menentukan akses.

## Bukti transfer
`transfer_proof`: id, invoice_id, student_id, guardian_id, reported_amount integer IDR, transfer_date, private_file_id, status (draft, pending, verified, rejected, withdrawn), submitted_at, verified_by, verified_at, rejection_reason dan created/updated timestamp. File di private storage, transaksi verifikasi yang disetujui menghubungkan payment terverifikasi secara unik; penarikan bukan penghapusan catatan finansial. Batasi relasi wali-anak dan scope kelas saat membaca atau menulis; uji otorisasi untuk file maupun data.
