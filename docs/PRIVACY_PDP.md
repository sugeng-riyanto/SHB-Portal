# Pelindungan data pribadi SHB Portal — rancangan implementasi

Status: acuan kerja, bukan sertifikat kepatuhan. UU No. 27 Tahun 2022 menyatakan data anak dan data keuangan pribadi sebagai data pribadi spesifik. UU tersebut mengatur pemrosesan data anak dengan persetujuan orang tua dan/atau wali sesuai peraturan; sekolah perlu menetapkan dan mendokumentasikan persetujuan/landasan yang berlaku, pemberitahuan dan cara menangani penarikan persetujuan. Rujukan resmi: https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022 dan https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/crc32/ . Tinjau peraturan pelaksana dan kebijakan yang relevan sebelum operasional.

## Kontrol yang direncanakan
- Tetapkan pengendali/prosesor, tujuan dan dasar pemrosesan, kategori data, pihak penerima termasuk penyedia cloud dan wilayah pemrosesan, waktu penyimpanan, serta kontak pengaduan sekolah; berikan pemberitahuan yang dapat dipahami wali.
- Simpan persetujuan orang tua/wali untuk pemrosesan data anak sesuai ketentuan yang berlaku; sediakan mekanisme pencatatan, bukti, perubahan dan tindak lanjut penarikan. Pastikan otoritas hubungan wali-anak sebelum akses.
- Batasi data pada yang diperlukan; akses role dan sekolah ditegakkan setiap operasi, audit akses super admin, lakukan MFA dan review akses berkala. Enkripsi saat transit dan simpan, termasuk backup, bukti bayar dan kredensial integrasi.
- Sediakan proses permintaan akses, perbaikan, penghapusan/penarikan sesuai ketentuan dan kewajiban retensi; catat tenggat, alasan penolakan yang sah dan pelaksanaan. Tetapkan retensi dan prosedur hapus arsip, backup serta vendor secara tertulis; tidak menggunakan angka retensi rekaan.
- Tetapkan petugas dan rencana respons insiden, pencatatan, penilaian dan pemberitahuan ke subjek dan lembaga sesuai ketentuan Pasal 46 (termasuk tenggat yang berlaku). Uji proses pemulihan, pembatasan insiden dan dokumentasi. Tentukan kewajiban penunjukan petugas PDP berdasarkan penerapan Pasal 53 dan putusan yang relevan.
- Nilai risiko transfer lintas negara dan penggunaan vendor; pembagian peran pengendali/prosesor dan perjanjian harus ditinjau sebelum data masuk. Hindari data nyata pada staging, logs, notifikasi contoh dan repo.

## Status teknis
Produksi wajib secret acak kuat, host eksplisit, debug mati, HTTPS, cookies aman dan proxy tepercaya; HSTS baru diaktifkan setelah HTTPS tervalidasi. Bukti transfer memakai akses berbasis hubungan serta header no-store. SQL hardening default deny belum diuji pada proyek Supabase. Kontrol lain pada daftar di atas **belum seluruhnya diimplementasikan atau diaudit**. Tidak ada dasar menyatakan aplikasi mematuhi UU PDP secara menyeluruh saat ini.
