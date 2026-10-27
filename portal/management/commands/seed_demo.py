from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from portal.models import Membership, School

class Command(BaseCommand):
    help = 'Create local demo accounts; only allowed on SQLite development databases.'
    def handle(self, *args, **options):
        if settings.PRODUCTION or settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError('Demo accounts are permitted only on a development SQLite database.')
        User = get_user_model()
        accounts = [
            ('superadmin@shb.sch.id', None),
            ('admin@shb.sch.id', Membership.Role.ADMIN),
            ('kepala@shb.sch.id', Membership.Role.PRINCIPAL),
            ('yayasan@shb.sch.id', Membership.Role.FOUNDATION),
            ('walikelas@shb.sch.id', Membership.Role.TEACHER),
            ('ortu@shb.sch.id', Membership.Role.GUARDIAN),
        ]
        with transaction.atomic():
            school, _ = School.objects.get_or_create(name='Sekolah Harapan Bangsa (Demo)')
            for username, role in accounts:
                # Never overwrite an existing user or password.
                user, created = User.objects.get_or_create(username=username, defaults={'email': username})
                if not created:
                    self.stdout.write(f'{username}: already exists; unchanged')
                    continue
                user.set_password('DemoSHB!2026')
                if role is None:
                    user.is_staff = True
                    user.is_superuser = True
                user.save()
                if role:
                    Membership.objects.create(user=user, school=school, role=role)
                self.stdout.write(f'{username}: created')
        self.stdout.write('Demo only: accounts have no real student data and must not be used in production.')
