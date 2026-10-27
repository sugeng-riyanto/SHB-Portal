# Kebutuhan produk

## Tujuan dan ruang lingkup
Admin mengunggah tagihan XLSX, memeriksa hasil, mengonfirmasi dan menjadwalkan pemberitahuan kepada orang tua/wali. Portal menampilkan tagihan, status pembayaran, pengumuman dan akun. Pengiriman dan pembayaran adalah dua status yang terpisah. MVP mencatat pembayaran yang diverifikasi admin; payment gateway, rekonsiliasi bank otomatis dan bukti unggahan merupakan opsi lanjutan, belum diasumsikan tersedia.

## Hak akses
| Fungsi | Admin sekolah | Kepala sekolah | Yayasan | Orang tua | Wali kelas |
|---|---|---|---|---|---|
| Murid, tahun, kelas, relasi wali | Kelola | Baca agregat | Baca agregat | Anak terhubung | Murid kelas ditugaskan |
| Tagihan dan pembayaran | Kelola, koreksi | Agregat | Agregat sesuai kewenangan | Anak terhubung | Ringkasan murid kelas ditugaskan sesuai kebijakan |
| Impor dan pengiriman | Kelola | Ringkasan | Ringkasan | Tidak | Tidak |
| Pengumuman | Buat, jadwalkan, cabut | Baca; kelola bila diberi izin | Baca | Sesuai sasaran | Sesuai sasaran |
| Akun dan penugasan | Kelola; tanpa melihat sandi | Profil sendiri | Profil sendiri | Profil sendiri | Profil sendiri |

Kepala sekolah dan yayasan default agregat; akses nominal individu hanya bila diberi izin terpisah secara eksplisit. Wali kelas tidak dapat mengubah nominal atau melihat kelas lain. Hak per sekolah/jenjang perlu dikonfigurasi; admin dibatasi lingkup yang ditugaskan.

## Dashboard responsif
- Admin: kartu jumlah tagihan, lunas, tunggakan, email gagal; histogram jumlah/nominal berdasarkan umur tunggakan, pie status tagihan, timeline jatuh tempo dan aktivitas impor; filter tahun, jenjang, kelas dan jenis.
- Kepala sekolah: tren bulanan tagihan, pembayaran terverifikasi, tunggakan agregat per jenjang/kelas; timeline dan komposisi status. Yayasan: agregat lintas jenjang dalam lingkup resmi, tren dan perbandingan per tahun.
- Wali kelas: status per siswa dalam kelas yang ditugaskan, ringkasan jumlah, timeline jatuh tempo; detail keuangan mengikuti kebijakan sekolah.
- Orang tua: pilih anak terhubung, tagihan dan rincian, pembayaran terverifikasi, total sisa, timeline jatuh tempo dan pengumuman relevan. Grafik hanya jika ada data yang berguna.
- Grafik wajib memiliki judul, satuan, periode, tabel alternatif dan keadaan kosong; jumlah dan nominal jangan dicampur. Data agregat yang kecil perlu perlindungan agar tidak mengungkap individu.

## Impor XLSX
Kolom diminta: nis/nisn, kelas, nama_murid, email, jenis_tagihan, nominal, denda, deskripsi. Tambahkan tahun_ajaran, periode_tagihan, tanggal_jatuh_tempo dan id_referensi_tagihan sebagai kolom yang disarankan; tanggal/jadwal wajib sebelum pengingat dikirim. Tetapkan format template dan definisi email sebagai email wali, bukan email murid, serta pemetaan banyak wali/murid. Identitas NIS/NISN disimpan sebagai teks untuk mempertahankan nol di depan. Semua nilai rupiah integer tanpa pecahan, >= 0; mata uang IDR; format tanggal ISO. Setiap baris di-preview dengan nomor dan alasan error; tidak mengirim email saat upload. Komit hanya baris valid yang secara eksplisit dipilih, atomik per batch terpilih; file yang sama tidak membuat duplikat. Idempotensi berdasar referensi stabil dan lingkup sekolah; konflik isi berbeda dihentikan untuk tinjauan, bukan menimpa otomatis. Alamat email input harus cocok dengan wali terverifikasi/diundang dan relasi anak sebelum pengiriman; perbedaan masuk antrean pemeriksaan. CSV injection dicegah saat ekspor. Batasi jenis, ukuran, jumlah baris dan proses file sebagai data tidak tepercaya.

## Proses keuangan
Status tagihan: draft, diterbitkan, dibatalkan; sisa dihitung dari pokok + denda yang berlaku - pembayaran terverifikasi - penyesuaian. Status lunas/sebagian/belum/terlambat diturunkan dari sisa dan jatuh tempo, bukan status email. Bayar sebagian, pembatalan/void, pengembalian dan koreksi memakai catatan terlacak; larang saldo negatif kecuali kebijakan kelebihan bayar disetujui. Admin mencatat tanggal, jumlah, metode dan referensi; cegah referensi ganda. Denda dibaca dari impor; otomatisasi denda belum ditetapkan. Ringkasan mencatat tanggal data terakhir.

## Murid dan tahun ajaran
CRUD murid, kontak dan relasi wali melalui identitas unik; murid dapat punya beberapa wali dan wali dapat punya beberapa anak. Simpan riwayat enrollment per tahun, kelas dan status; kelas hanya sekali aktif dalam satu tahun sesuai jenjang. Persiapkan tahun baru, preview pemetaan kenaikan tiap murid, identifikasi tinggal kelas/pindah, lalu konfirmasi; transaksi idempotent. Kelas 9 dan 12 dapat lulus, tetapi kenaikan SMP ke SMA tidak diasumsikan otomatis: keputusan sekolah. Lulus/nonaktif mempertahankan tagihan dan histori. Reset berarti arsip/nonaktif atau reset lingkungan uji, bukan hapus permanen data keuangan; setiap operasi berisiko harus terotorisasi, ada preview, audit, cadangan dan mekanisme pemulihan.

## Akun dan pengumuman
Undangan aman satu kali, kedaluwarsa; wali menetapkan kata sandi. Lupa sandi memakai tautan sekali pakai, respons generik, pembatasan percobaan dan audit; jangan kirim password via email. Orang tua hanya melihat anak yang diverifikasi; perubahan email mengharuskan verifikasi ulang. Pengumuman memiliki judul, isi, target role/jenjang/kelas, waktu terbit, kedaluwarsa, penulis dan status draft/terbit/cabut; re-evaluasi izin saat dibaca. Email pengumuman opsional dengan preview, sasaran dan audit; tidak menggunakan CC yang membocorkan alamat.

## Kriteria penerimaan
1. Dua wali dan dua murid diuji silang: tidak ada akses data anak lain, termasuk API, ekspor dan grafik.
2. Impor valid sukses, salah menjelaskan baris; unggah ulang identik tidak menggandakan tagihan dan tidak otomatis mengirim.
3. Pembayaran sebagian, lunas, koreksi dan pembatalan menghasilkan saldo serta histori yang benar; email sukses tidak mengubah saldo.
4. Kenaikan/kelulusan mempertahankan riwayat dan saldo; reset tidak menghapus histori keuangan.
5. Tautan aktivasi/reset aman, kedaluwarsa dan tidak mengungkap apakah akun ada; pengiriman gagal dapat ditindaklanjuti tanpa menggandakan notifikasi.
6. Dashboard menghormati peran dan lingkup pada ponsel dan desktop; pengumuman hanya muncul pada sasaran.

## Perubahan yang disepakati — SHB Portal
Nama portal SHB Portal; bahasa Indonesia dan English, light/dark, font besar, sidebar dan main content menurut lima peran. Admin upload dan download template XLSX serta ekspor terfilter, mengelola filter dan pembagian undangan akun secara aman. Pengiriman pesan ke inbox, email dan pilihan WhatsApp resmi tersedia untuk semua wali, kelas, individu atau daftar pilihan; personalisasi dan status masing-masing penerima/kanal, preview sebelum kirim. Lihat PROJECT_CONSTITUTION.md dan COMMUNICATION_AND_ACCOUNTS.md untuk detail dan batasan. Fungsi belum diimplementasikan.

## Rekening, VA, dan saudara kandung
Kepala sekolah dapat membuat, membaca, mengubah dan menonaktifkan rekening sekolah; admin mengimpor referensi rekening dan nomor VA opsional dalam XLSX. Tujuan pembayaran pada tagihan harus akurat dan berjejak. Wali menggunakan satu akun untuk anak-anak yang telah terhubung dan dapat memilih anak; tiap anak tetap bisa terhubung 1–3 wali. Lihat konstitusi untuk validasi dan perlindungan histori.

## Bukti transfer dan salin VA
Wali memilih anak/tagihan, menyalin VA, unggah foto, isi nominal dan tanggal. Pemilik melihat/ubah/tarik bukti menunggu; setelah verifikasi, koreksi via admin dan audit. Admin, wali kelas ditugaskan dan kepala sekolah dalam scope dapat preview gambar dan nominal; admin memverifikasi/menolak secara eksplisit. Bukti belum diverifikasi tidak mengubah saldo. Lihat konstitusi untuk kontrol file dan akses.

## Dashboard dan batas tagihan
Semua dashboard, sidebar dan menu mengikuti matriks RBAC_MATRIX.md; alert jatuh tempo dan terlambat dibatasi scope. Tombol WhatsApp admin selalu tersedia, memakai nomor resmi yang diatur dan diverifikasi sekolah. Alur chat pengguna terpisah dari pengiriman otomatis. Nilai hari sebelum jatuh tempo belum ditetapkan.
