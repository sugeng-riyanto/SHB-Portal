# Deployment dan CI/CD

Rencana: repository Git privat sesuai kebutuhan → CI lint, unit, integration dan security → staging dengan data sintetis → uji dan persetujuan rilis → produksi. Bangun artefak versi tetap; migrasi yang kompatibel dilakukan setelah backup terverifikasi, dengan rencana rollback aplikasi dan prosedur pemulihan database. Rahasia tersedia hanya melalui secret manager; pisahkan proyek Supabase dan kredensial Gmail tiap lingkungan. Tidak ada alamat produksi atau perintah deploy yang telah diverifikasi. Tentukan hosting, domain, HTTPS, akses operasi, biaya dan batas kapasitas sebelum implementasi. Jadwalkan worker dan monitor; gunakan mailbox pengujian di staging. Jangan mengirim massal atau menjalankan migrasi produksi sebelum release gates terpenuhi.

## portal.scangrade.web.id (nginx + gunicorn)
Artefak pemasangan yang konkret ada di `deploy/`: vhost nginx, unit systemd untuk gunicorn, template environment, dan skrip diagnosa. Diagnosis 403 yang diukur dari luar, langkah pemasangan, dan perintah verifikasinya ada di `deploy/README.md`. Konfigurasi itu belum dieksekusi di server produksi dari sesi ini; validasi dengan `nginx -t` sebelum reload.
