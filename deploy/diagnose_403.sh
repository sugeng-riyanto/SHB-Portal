#!/usr/bin/env bash
# Diagnosa 403 pada https://portal.scangrade.web.id/ — HANYA MEMBACA.
# Jalankan di server: sudo bash deploy/diagnose_403.sh
# Script ini tidak mengubah konfigurasi, tidak me-restart layanan, dan tidak
# mencetak isi berkas rahasia.
set -uo pipefail

HOST="portal.scangrade.web.id"
UPSTREAM="127.0.0.1:8001"

echo "== 1. Apakah permintaan sampai ke nginx atau ke aplikasi? =="
for path in / /accounts/login/ /robots.txt /tidak-ada-abc; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --resolve "$HOST:443:127.0.0.1" "https://$HOST$path" 2>/dev/null || echo "gagal")
  echo "   $path -> $code"
done
echo "   (403 di SEMUA path, termasuk yang tidak ada = nginx menolak sebelum proxy)"

echo
echo "== 2. Apakah upstream Django hidup? =="
if command -v ss >/dev/null; then ss -ltnp 2>/dev/null | grep -F "$UPSTREAM" || echo "   tidak ada listener di $UPSTREAM"; fi
curl -s -o /dev/null -w '   http://%{remote_ip}:%{remote_port} -> %{http_code}\n' "http://$UPSTREAM/" 2>/dev/null || echo "   upstream tidak menjawab"

echo
echo "== 3. Server block mana yang melayani host ini? =="
nginx -T 2>/dev/null | awk -v h="$HOST" '
  /^server[[:space:]]*\{/ {buf=""; inside=1}
  inside {buf=buf $0 "\n"}
  inside && /server_name/ && index($0,h) {found=1}
  inside && /^\}/ {if(found){print buf; found=0}; inside=0}
' | sed -n '1,60p' | sed 's/^/   /'
echo "   Jika blok di atas memuat 'deny all', 'return 403', atau tidak punya"
echo "   proxy_pass, itulah penyebab 403 — ganti dengan deploy/nginx/portal.scangrade.web.id.conf."

echo
echo "== 4. Hak akses direktori (403 untuk semua path juga muncul bila www-data tidak bisa menembus direktori) =="
for d in /srv/shb-portal /srv/shb-portal/staticfiles /var/www /var/www/html; do
  [ -e "$d" ] && namei -l "$d" | sed 's/^/   /' || echo "   $d tidak ada"
done

echo
echo "== 5. Log nginx (20 baris terakhir) =="
for f in /var/log/nginx/portal.error.log /var/log/nginx/error.log; do
  [ -r "$f" ] && { echo "   --- $f ---"; tail -n 20 "$f" | sed 's/^/   /'; }
done

echo
echo "== 6. Layanan aplikasi =="
systemctl is-active shb-portal 2>/dev/null | sed 's/^/   shb-portal: /'
[ -r /etc/shb-portal.env ] && echo "   /etc/shb-portal.env ada, izin: $(stat -c '%a %U:%G' /etc/shb-portal.env)" || echo "   /etc/shb-portal.env tidak ada"

echo
echo "Selesai. Tidak ada perubahan yang dilakukan."
