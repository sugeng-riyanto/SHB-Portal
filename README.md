# SHB Portal — fondasi awal

Ini awal proyek, belum aplikasi produksi. Termasuk aturan domain awal untuk nominal IDR, status dan pengingat tagihan, dan contoh otorisasi berdasar scope; serta preview UI dan dokumen kebutuhan. Semua keputusan akses harus ditegakkan ulang di backend dan database, tidak cukup dengan fungsi domain ini.

Jalankan tes Python 3.10+: `PYTHONPATH=src python3 -m unittest discover -s tests -v`.

Belum tersedia: Django, Supabase Auth/RLS, database, migrasi, import XLSX, upload privat, pesan email/WhatsApp, bilingual lengkap, RBAC server, ataupun deployment. Jangan gunakan data nyata atau melakukan rilis dari fondasi ini. Lihat docs/PROJECT_CONSTITUTION.md dan docs/AI_HANDOFF.md.
