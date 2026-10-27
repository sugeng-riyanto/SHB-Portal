"""Seed synthetic demo data so the local preview can be rebuilt from scratch.

All values here are fabricated. Never load real student, guardian or payment data with
this command, and never expose the demo accounts outside a development machine.

    python manage.py migrate
    python manage.py seed_demo

Running it again only fills in what is missing, so it is safe to repeat after a
worktree restore. It refuses to run when settings.PRODUCTION is active (SHB_ENV=production).
"""
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

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
DEMO_PASSWORD = 'shb-preview-2026'
DEMO_USERS = (
    {'username': 'admin', 'first_name': 'Admin', 'email': 'admin@contoh.id',
     'role': Membership.Role.ADMIN, 'admin_site': True},
    {'username': 'walikelas', 'first_name': 'Wali Kelas', 'email': 'wali7a@contoh.id',
     'role': Membership.Role.TEACHER, 'admin_site': False},
    {'username': 'ortu', 'first_name': 'Orang Tua', 'email': 'ortu@contoh.id',
     'role': Membership.Role.GUARDIAN, 'admin_site': False},
)
DEMO_CLASSES = (
    {'name': '7A', 'teachers': ('walikelas',)},
    {'name': '10N', 'teachers': ('walikelas',)},
)
DEMO_STUDENTS = (
    {'nis': '2026001', 'name': 'Murid Contoh 1', 'classroom': '7A', 'guardians': ('ortu',)},
    {'nis': '2026002', 'name': 'Murid Contoh 2', 'classroom': '7A', 'guardians': ('ortu',)},
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
    help = 'Membuat data contoh sintetis untuk preview lokal; aman dijalankan berulang.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            default=DEMO_PASSWORD,
            help='Kata sandi akun contoh yang baru dibuat. Gunakan kata sandi demo saja.',
        )

    def handle(self, *args, **options):
        if settings.PRODUCTION:
            raise CommandError('seed_demo tidak dijalankan pada SHB_ENV=production.')
        created = []
        User = get_user_model()

        school, _ = School.objects.get_or_create(name=DEMO_SCHOOL_NAME)
        year, _ = AcademicYear.objects.get_or_create(school=school, label=DEMO_YEAR_LABEL)

        users = {}
        for spec in DEMO_USERS:
            user, is_new = User.objects.get_or_create(
                username=spec['username'],
                defaults={'email': spec['email'], 'first_name': spec['first_name']},
            )
            if is_new:
                user.set_password(options['password'])
                user.is_staff = spec['admin_site']
                user.is_superuser = spec['admin_site']
                user.save()
                created.append(f'user {spec["username"]}')
            users[spec['username']] = user
            _, is_new = Membership.objects.get_or_create(
                user=user, school=school, role=spec['role'])
            if is_new:
                created.append(f'membership {spec["username"]}/{spec["role"]}')

        classrooms = {}
        for spec in DEMO_CLASSES:
            classroom, is_new = Classroom.objects.get_or_create(year=year, name=spec['name'])
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
            self.stdout.write(self.style.SUCCESS('Data contoh sudah lengkap; tidak ada perubahan.'))
        self.stdout.write(
            f'Sekolah: {school.name} · tahun {year.label} · '
            f'{Student.objects.filter(school=school).count()} murid · '
            f'{Invoice.objects.filter(enrollment__student__school=school).count()} tagihan')
        self.stdout.write(
            'Akun contoh: admin, walikelas, ortu. '
            'Kata sandi mengikuti opsi --password (lihat --help).')
