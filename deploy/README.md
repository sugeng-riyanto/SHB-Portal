# Deploy SHB Portal di portal.scangrade.web.id

Dokumen ini untuk satu tujuan: halaman `403 Forbidden` dari nginx pada
`https://portal.scangrade.web.id/` tidak lagi terjadi. Isinya diagnosis yang
sudah terbukti dari luar, langkah pemasangan, dan cara memverifikasi.

## Diagnosis: 403 itu berasal dari nginx, bukan dari Django

Diukur dari jaringan luar pada 30 Oktober 2026:

| Bukti | Hasil | Artinya |
|---|---|---|
| `GET https://portal.scangrade.web.id/` | `403`, header `server: nginx/1.18.0 (Ubuntu)`, badan 162 byte halaman bawaan nginx | Django tidak pernah dihubungi; jawaban ini dibuat nginx |
| Semua path (`/`, `/accounts/login/`, `/static/…`, `/robots.txt`, `/.well-known/…`, path acak) | **403 semuanya** | Bukan masalah route aplikasi; nginx menolak di level lokasi/server |
| `Host: scangrade.web.id` ke IP yang sama | **200** | Mesin dan nginx sehat, dan ada vhost lain yang berfungsi |
| `Host: unknown-host.example` | 502 | Vhost default mem-proxy ke upstream yang mati |
| `http://portal.scangrade.web.id/` (port 80) | 404 | Tidak ada vhost port 80 untuk host ini |
| Sertifikat TLS | sah, `CN=portal.scangrade.web.id`, Let's Encrypt, s.d. 26 Jan 2027 | TLS bukan penyebabnya |
| Apex `scangrade.web.id` | aplikasi lain ("ScanGrade — Digital Exam Platform", Express + Supabase) | Portal bukan aplikasi yang sama; jangan menumpangkannya di vhost itu |

Penyebab yang konsisten dengan semua gejala di atas, berurutan menurut
kemungkinan:

1. Server block `portal.scangrade.web.id` memuat `deny all`, `return 403`, atau
   `limit_except` yang menolak semua, dan tidak punya `proxy_pass`.
2. Server block punya `root` ke direktori yang tidak bisa ditembus `www-data`
   (nginx menjawab 403 untuk setiap path di bawahnya, termasuk path yang tidak ada).
3. Server block hanya berisi `root` tanpa `index`, sehingga direktori dianggap
   terlarang — tetapi ini biasanya memberi 404 untuk path yang tidak ada, jadi
   kurang cocok dengan gejala "403 di semua path".

`deploy/diagnose_403.sh` membedakan ketiganya dalam satu kali jalan.

## Reproduksi artefak yang dibutuhkan

Dijalankan di server, sebagai root, dari checkout repositori ini:

```bash
sudo apt-get install -y python3-venv nginx
sudo mkdir -p /srv/shb-portal && sudo chown -R www-data:www-data /srv/shb-portal
# salin checkout ke /srv/shb-portal, lalu:
cd /srv/shb-portal
sudo -u www-data python3 -m venv .venv
sudo -u www-data .venv/bin/pip install -r requirements.txt
sudo -u www-data .venv/bin/python manage.py collectstatic --noinput
```

`requirements.txt` memuat `gunicorn` untuk menjalankan aplikasi; `daphne`
tetap hanya untuk preview lokal.

Environment: salin `deploy/shb-portal.env.example` ke `/etc/shb-portal.env`,
isi nilainya di server, lalu `chown root:root` dan `chmod 600`. Nilai rahasia
tidak pernah masuk repositori. Tanpa `DJANGO_ALLOWED_HOSTS` yang memuat
`portal.scangrade.web.id`, Django menjawab **400**; tanpa
`DJANGO_CSRF_TRUSTED_ORIGINS=https://portal.scangrade.web.id`, POST login
ditolak **403 CSRF** — keduanya berbeda dari 403 nginx dan hanya muncul
setelah proxy benar.

## Pemasangan

```bash
# 1. Aplikasi
sudo .venv/bin/python manage.py migrate
sudo cp deploy/systemd/shb-portal.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now shb-portal
sudo systemctl status shb-portal --no-pager      # harus active (running)

# 2. nginx: ganti server block yang menolak dengan yang ini
sudo cp deploy/nginx/portal.scangrade.web.id.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/portal.scangrade.web.id.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/<blok-lama-yang-menolak>
sudo nginx -t && sudo systemctl reload nginx
```

## Verifikasi

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8001/                     # 200/302 dari aplikasi
curl -s -o /dev/null -w '%{http_code}\n' https://portal.scangrade.web.id/           # 200/302, bukan 403
curl -s -o /dev/null -w '%{http_code}\n' https://portal.scangrade.web.id/accounts/login/   # 200
curl -s https://portal.scangrade.web.id/accounts/login/ | grep -c csrfmiddlewaretoken     # 1
curl -s -o /dev/null -w '%{http_code}\n' https://portal.scangrade.web.id/static/portal/app.css  # 200
```

Lalu uji login penuh di browser: POST form harus **302 ke `/dashboard/`**, bukan
403. Bila 400, periksa `DJANGO_ALLOWED_HOSTS`; bila 403 CSRF, periksa
`DJANGO_CSRF_TRUSTED_ORIGINS` dan `DJANGO_TRUST_PROXY_HTTPS=1`. Jangan
menonaktifkan CSRF.

## Batasan

Vhost apex `scangrade.web.id` menjalankan aplikasi lain; jangan mengubahnya
untuk portal ini. Port 80 untuk host ini sebelumnya tidak punya vhost, sehingga
blok HTTP di konfigurasi ini perlu dipasang bersama blok HTTPS agar redirect dan
renewal ACME bekerja.

Konfigurasi ini belum diuji dengan `nginx -t` di mesin nyata dari sesi ini:
VM kerja tidak menjalankan nginx dan tidak punya akses ke server
`103.93.133.193`. Validasi wajib dilakukan di server sebelum reload.

## Verifikasi setelah memasang konfigurasi

```bash
./deploy/verify_deploy.sh            # dari mesin mana pun
./deploy/verify_deploy.sh --loopback # dari server, sekalian uji 127.0.0.1
```

Skrip ini gagal (exit 1) bila port 80 tidak mengalihkan ke HTTPS, atau bila port 443 masih
menjawab halaman galat nginx alih-alih aplikasi, dan mencetak petunjuk sesuai pola kegagalan.
