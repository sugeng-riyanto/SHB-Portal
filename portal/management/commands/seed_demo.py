"""Seed synthetic demo data for the local preview.

All values here are fabricated. Never load real student, guardian or payment data with
this command, and never expose these accounts outside a development machine.

    python manage.py migrate
    python manage.py seed_demo

Creates demo accounts that can sign in, together with example classes, students,
invoices and a bank account so the preview has something to render. Running it again
fills in only what is missing and resets the password of the six reserved demo
accounts to the requested demo password; accounts with a different email are never
touched. The command refuses to run unless the database is a
SQLite development database and settings.PRODUCTION is off.
"""
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from portal.models import (
    AcademicYear,
    BankAccount,
    Classroom,
    Enrollment,
    Invoice,
    Membership,
    School,
    Student,
)

DEMO_SCHOOL_NAME = 'Sekolah Harapan Bangsa (contoh)'
DEMO_YEAR_LABEL = '2026/2027'
DEMO_PASSWORD = 'demo123'
# (username, role): role None means the portal superuser.
DEMO_ACCOUNTS = (
    ('superadmin@shb.sch.id', None),
    ('admin@shb.sch.id', Membership.Role.ADMIN),
    ('kepala@shb.sch.id', Membership.Role.PRINCIPAL),
    ('yayasan@shb.sch.id', Membership.Role.FOUNDATION),
    ('walikelas@shb.sch.id', Membership.Role.TEACHER),
    ('ortu@shb.sch.id', Membership.Role.GUARDIAN),
)
DEMO_CLASSES = (
    {'name': '7A', 'teachers': ('walikelas@shb.sch.id',)},
    {'name': '10N', 'teachers': ('walikelas@shb.sch.id',)},
)
DEMO_STUDENTS = (
    {'nis': '2026001', 'name': 'Murid Contoh 1', 'classroom': '7A',
     'guardians': ('ortu@shb.sch.id',)},
    {'nis': '2026002', 'name': 'Murid Contoh 2', 'classroom': '7A',
     'guardians': ('ortu@shb.sch.id',)},
    {'nis': '2026003', 'name': 'Murid Contoh 3', 'classroom': '10N', 'guardians': ()},
)
DEMO_INVOICES = (
    {'nis': '2026001', 'reference': 'DEMO-2026-0001', 'description': 'SPP Oktober 2026',
     'amount': 500000, 'due_date': date(2026, 10, 30), 'virtual_account': '8800123456789001'},
    {'nis': '2026002', 'reference': 'DEMO-2026-0002', 'description': 'SPP Oktober 2026',
     'amount': 500000, 'due_date': date(2026, 10, 30), 'virtual_account': '8800123456789002'},
    {'nis': '2026003', 'reference': 'DEMO-2026-0003', 'description': 'Kegiatan sekolah',
     'amount': 450000, 'due_date': date(2026, 11, 5), 'virtual_account': '8800123456789003'},
)
DEMO_BANK_ACCOUNT = {'bank_name': 'Bank Contoh A', 'account_name': 'Yayasan SHB',
                     'account_number': '1234567890'}


class Command(BaseCommand):
    help = 'Create local demo accounts and example school data; SQLite development only.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            default=DEMO_PASSWORD,
            help='Kata sandi untuk keenam akun demo, disetel ulang setiap kali dijalankan.',
        )

    def handle(self, *args, **options):
        engine = settings.DATABASES['default']['ENGINE']
        if settings.PRODUCTION or engine != 'django.db.backends.sqlite3':
            raise CommandError(
                'Demo accounts are permitted only on a development SQLite database.')
        created = []
        User = get_user_model()

        with transaction.atomic():
            school, is_new = School.objects.get_or_create(name=DEMO_SCHOOL_NAME)
            if is_new:
                created.append(f'sekolah {school.name}')
            year, is_new = AcademicYear.objects.get_or_create(
                school=school, label=DEMO_YEAR_LABEL)
            if is_new:
                created.append(f'tahun ajaran {year.label}')

            users = {}
            for username, role in DEMO_ACCOUNTS:
                # The six reserved demo accounts are reset on purpose: the owner asked
                # for this fixed demo password. An account whose email differs from the
                # username is a real account, so it is never touched.
                user, is_new = User.objects.get_or_create(
                    username=username, defaults={'email': username})
                if not is_new and user.email != username:
                    raise CommandError(
                        f'{username}: akun yang sudah ada memakai email lain; tidak diubah')
                user.set_password(options['password'])
                if role is None:
                    user.is_staff = True
                    user.is_superuser = True
                user.save()
                users[username] = user
                self.stdout.write(
                    f'{username}: dibuat' if is_new else f'{username}: password disetel ulang')
                if role and Membership.objects.get_or_create(
                        user=user, school=school, role=role)[1]:
                    created.append(f'peran {username}/{role}')
            classrooms = {}
            for spec in DEMO_CLASSES:
                classroom, is_new = Classroom.objects.get_or_create(
                    year=year, name=spec['name'])
                if is_new:
                    created.append(f'kelas {spec["name"]}')
                for username in spec['teachers']:
                    classroom.teachers.add(users[username])
                classrooms[spec['name']] = classroom

            students = {}
            for spec in DEMO_STUDENTS:
                student, is_new = Student.objects.get_or_create(
                    school=school, nis=spec['nis'], defaults={'name': spec['name']})
                if is_new:
                    created.append(f'murid {spec["nis"]}')
                for username in spec['guardians']:
                    student.guardians.add(users[username])
                students[spec['nis']] = student

            enrollments = {}
            for spec in DEMO_STUDENTS:
                enrollment, is_new = Enrollment.objects.get_or_create(
                    student=students[spec['nis']], classroom=classrooms[spec['classroom']])
                enrollments[spec['nis']] = enrollment
                if is_new:
                    created.append(f'enrollment {spec["nis"]}')

            for spec in DEMO_INVOICES:
                _, is_new = Invoice.objects.get_or_create(
                    reference=spec['reference'],
                    defaults={
                        'enrollment': enrollments[spec['nis']],
                        'description': spec['description'],
                        'amount': spec['amount'],
                        'due_date': spec['due_date'],
                        'virtual_account': spec['virtual_account'],
                    },
                )
                if is_new:
                    created.append(f'tagihan {spec["reference"]}')

            _, is_new = BankAccount.objects.get_or_create(
                school=school,
                bank_name=DEMO_BANK_ACCOUNT['bank_name'],
                account_number=DEMO_BANK_ACCOUNT['account_number'],
                defaults={'account_name': DEMO_BANK_ACCOUNT['account_name']},
            )
            if is_new:
                created.append('rekening bank contoh')

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Data contoh siap: {len(created)} objek baru dibuat.'))
            for item in created:
                self.stdout.write(f'  + {item}')
        else:
            self.stdout.write(self.style.SUCCESS(
                'Data contoh sudah lengkap; tidak ada perubahan.'))
        self.stdout.write(
            f'{school.name} · tahun {year.label} · '
            f'{Student.objects.filter(school=school).count()} murid · '
            f'{Invoice.objects.filter(enrollment__student__school=school).count()} tagihan')
        self.stdout.write(
            'Akun contoh: ' + ', '.join(username for username, _ in DEMO_ACCOUNTS) + '.')
        self.stdout.write('Demo only: data sintetis untuk preview lokal, bukan data sekolah.')
