from datetime import date
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from portal.models import AcademicYear, Classroom, Enrollment, Invoice, Membership, School, Student

class Command(BaseCommand):
    help = 'Create non-sensitive demo students and invoices in local SQLite only.'
    def handle(self,*args,**options):
        if settings.PRODUCTION or settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError('Demo data is only allowed in local development SQLite.')
        User=get_user_model()
        guardian=User.objects.filter(username='ortu@shb.sch.id',is_active=True).first()
        teacher=User.objects.filter(username='walikelas@shb.sch.id',is_active=True).first()
        school=School.objects.filter(name='Sekolah Harapan Bangsa (Demo)').first()
        if not guardian or not teacher or not school or not Membership.objects.filter(user=guardian,school=school,role=Membership.Role.GUARDIAN,active=True).exists():
            raise CommandError('Run seed_demo first and ensure the demo guardian membership is active.')
        with transaction.atomic():
            year,_=AcademicYear.objects.get_or_create(school=school,label='DEMO 2026/2027')
            classroom,_=Classroom.objects.get_or_create(year=year,name='8A')
            classroom.teachers.add(teacher)
            student,_=Student.objects.get_or_create(school=school,nis='DEMO-001',defaults={'name':'Murid Contoh 1'})
            student.guardians.add(guardian)
            enrollment,_=Enrollment.objects.get_or_create(student=student,classroom=classroom)
            invoice,created=Invoice.objects.get_or_create(reference='SHB-DEMO-INV-001',defaults={'enrollment':enrollment,'description':'SPP Oktober 2026 (Demo)','amount':500000,'fine':0,'due_date':date(2026,10,31),'virtual_account':'0000000000000000'})
            if not created and invoice.enrollment_id != enrollment.id:
                raise CommandError('Demo invoice reference is already in use elsewhere.')
        self.stdout.write(self.style.SUCCESS('Demo invoice ready. Log in as ortu@shb.sch.id and open it from the dashboard.'))
