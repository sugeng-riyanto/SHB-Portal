# SHB Portal — fondasi awal

Ini awal proyek, belum aplikasi produksi. Termasuk aturan domain awal untuk nominal IDR, status dan pengingat tagihan, dan contoh otorisasi berdasar scope; serta preview UI dan dokumen kebutuhan. Semua keputusan akses harus ditegakkan ulang di backend dan database, tidak cukup dengan fungsi domain ini.

Jalankan tes Python 3.10+: `PYTHONPATH=src python3 -m unittest discover -s tests -v`.

Belum tersedia: Django, Supabase Auth/RLS, database, migrasi, import XLSX, upload privat, pesan email/WhatsApp, bilingual lengkap, RBAC server, ataupun deployment. Jangan gunakan data nyata atau melakukan rilis dari fondasi ini. Lihat docs/PROJECT_CONSTITUTION.md dan docs/AI_HANDOFF.md.

## Development web foundation
Django basic sign-in, logout, school membership, student/class/enrollment/invoice models, and read-only role-scoped dashboard are available for local development. `python manage.py migrate` then `python manage.py test portal` after installing requirements. SQLite is the development default; `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, optional `POSTGRES_PORT` configure a TLS PostgreSQL connection. Do not apply these migrations to an existing Supabase project without identifying and isolating the intended project and reviewing security.

This prototype currently uses Django auth, **not Supabase Auth**, and does not configure Supabase RLS; the database connector is not a complete Supabase integration. Disable Data API exposure until policies and integration tests exist. Do not deploy, use real student data, or expose it publicly. Set a strong `DJANGO_SECRET_KEY`, configure hosts and HTTPS before production. Account activation, recovery, role management, receipts, XLSX, notifications and complete visual design remain pending.
