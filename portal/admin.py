"""Restricted internal management; server-side authorization remains mandatory."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import School, Membership, AcademicYear, Classroom, Student, Enrollment, Invoice, Payment, TransferProof, SchoolUpdate

# The standard admin login permits staff; restrict this site's entire interface.
admin.site.has_permission = lambda request: bool(request.user.is_active and request.user.is_superuser)
admin.site.site_header = 'SHB Portal · Super Admin'
admin.site.site_title = 'SHB Portal'
admin.site.index_title = 'Pengelolaan sekolah dan pengguna'
admin.site.register(School)
admin.site.register(Membership)
admin.site.register(SchoolUpdate)
# User administration is provided by Django and restricted by has_permission above.
