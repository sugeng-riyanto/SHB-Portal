from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import School, Membership, AcademicYear, Classroom, Student, Enrollment, Invoice

class DashboardAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.guardian = User.objects.create_user(username='guardian',password='long-test-password')
        self.teacher = User.objects.create_user(username='teacher',password='long-test-password')
        self.other = User.objects.create_user(username='other',password='long-test-password')
        self.school = School.objects.create(name='SHB')
        self.other_school = School.objects.create(name='Other')
        year = AcademicYear.objects.create(school=self.school,label='2026/27')
        self.classroom = Classroom.objects.create(year=year,name='8A')
        self.classroom.teachers.add(self.teacher)
        self.student = Student.objects.create(school=self.school,nis='001',name='ANAK SATU')
        self.student.guardians.add(self.guardian)
        enrollment = Enrollment.objects.create(student=self.student,classroom=self.classroom)
        Invoice.objects.create(enrollment=enrollment,reference='INV-1',description='SPP',amount=500000,due_date=date(2026,11,1))
        Membership.objects.create(user=self.guardian,school=self.school,role='guardian')
        Membership.objects.create(user=self.teacher,school=self.school,role='teacher')
        Membership.objects.create(user=self.other,school=self.other_school,role='admin')
    def test_login_required(self):
        self.assertRedirects(self.client.get('/dashboard/'),'/accounts/login/?next=/dashboard/')
    def test_linked_guardian_sees_invoice(self):
        self.client.force_login(self.guardian)
        self.assertContains(self.client.get('/dashboard/'),'ANAK SATU')
    def test_assigned_teacher_sees_invoice(self):
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get('/dashboard/'),'ANAK SATU')
    def test_other_school_admin_cannot_see_invoice(self):
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get('/dashboard/'),'ANAK SATU')
    def test_revoked_membership_denies_access(self):
        Membership.objects.filter(user=self.guardian).update(active=False)
        self.client.force_login(self.guardian)
        self.assertNotContains(self.client.get('/dashboard/'),'ANAK SATU')
    def test_logout_requires_post(self):
        self.client.force_login(self.guardian)
        self.assertEqual(self.client.get(reverse('logout')).status_code,405)

    def test_principal_and_foundation_see_only_aggregate(self):
        User = get_user_model()
        for role in ('principal', 'foundation'):
            user = User.objects.create_user(username=role,password='long-test-password')
            Membership.objects.create(user=user,school=self.school,role=role)
            self.client.force_login(user)
            response = self.client.get('/dashboard/')
            self.assertNotContains(response, 'ANAK SATU')
            self.assertContains(response, '500000')
    def test_wrong_school_principal_has_no_aggregate(self):
        user = get_user_model().objects.create_user(username='otherprincipal',password='long-test-password')
        Membership.objects.create(user=user,school=self.other_school,role='principal')
        self.client.force_login(user)
        self.assertNotContains(self.client.get('/dashboard/'), '500000')
    def test_other_guardian_and_unassigned_teacher_cannot_see(self):
        User = get_user_model()
        for role in ('guardian', 'teacher'):
            user = User.objects.create_user(username='unassigned-'+role,password='long-test-password')
            Membership.objects.create(user=user,school=self.school,role=role)
            self.client.force_login(user)
            self.assertNotContains(self.client.get('/dashboard/'), 'ANAK SATU')
    def test_cross_school_invalid_enrollment_is_not_visible(self):
        year = AcademicYear.objects.create(school=self.other_school,label='2026/27')
        other_class = Classroom.objects.create(year=year,name='9A')
        other_class.teachers.add(self.teacher)
        bad = Enrollment.objects.create(student=self.student,classroom=other_class)
        Invoice.objects.create(enrollment=bad,reference='BAD',description='CROSS SCHOOL LEAK',amount=999,due_date=date(2026,11,1))
        self.client.force_login(self.guardian)
        self.assertNotContains(self.client.get('/dashboard/'),'CROSS SCHOOL LEAK')
        self.client.force_login(self.teacher)
        self.assertNotContains(self.client.get('/dashboard/'),'CROSS SCHOOL LEAK')
    def test_admin_sees_only_own_school(self):
        user = get_user_model().objects.create_user(username='adminshb',password='long-test-password')
        Membership.objects.create(user=user,school=self.school,role='admin')
        self.client.force_login(user)
        self.assertContains(self.client.get('/dashboard/'),'ANAK SATU')

    def test_local_static_assets_and_viewport(self):
        response = self.client.get('/')
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, '/static/portal/app.css')
        self.assertContains(response, '/static/portal/app.js')
        self.assertNotContains(response, 'cdn.')

    def test_xlsx_import_requires_admin(self):
        self.client.force_login(self.guardian)
        self.assertEqual(self.client.get('/imports/').status_code,403)
        self.assertEqual(self.client.get('/imports/template.xlsx').status_code,403)
    def test_admin_download_and_preview(self):
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        from openpyxl import load_workbook
        user = get_user_model().objects.create_user(username='admin_import',password='long-test-password')
        Membership.objects.create(user=user,school=self.school,role='admin')
        self.client.force_login(user)
        template = self.client.get('/imports/template.xlsx')
        self.assertEqual(template.status_code,200)
        book = load_workbook(BytesIO(template.content))
        book.active.append(['001','8A','ANAK SATU','a@example.test','SPP',500000,0,'','2026/27','Oktober','2026-11-01','ref-001','','00001234'])
        stream=BytesIO();book.save(stream)
        upload=SimpleUploadedFile('data.xlsx',stream.getvalue())
        result=self.client.post('/imports/',{'file':upload})
        self.assertContains(result,'Validasi awal lolos')
        self.assertContains(result,'001')
        self.assertEqual(Invoice.objects.count(),1)
    def test_formula_rejected_in_preview(self):
        from io import BytesIO
        from openpyxl import load_workbook
        from .imports import template_bytes,preview_xlsx
        book=load_workbook(BytesIO(template_bytes()))
        book.active.append(['001','8A','Nama','a@example.test','SPP','=1+1',0,'','2026/27','Oktober','2026-11-01','ref','',''])
        stream=BytesIO();book.save(stream)
        self.assertTrue(any('Formula' in e for e in preview_xlsx(stream.getvalue())[0]['errors']))

    def test_guardian_upload_and_cross_family_privacy(self):
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        from .models import TransferProof, Payment
        image=BytesIO();Image.new('RGB',(4,4),'white').save(image,format='PNG')
        self.client.force_login(self.guardian)
        response=self.client.post('/invoices/1/proof/',{'amount':'200000','transfer_date':'2026-10-27','image':SimpleUploadedFile('proof.png',image.getvalue())})
        self.assertEqual(response.status_code,302)
        proof=TransferProof.objects.get()
        self.assertEqual(Payment.objects.count(),0)
        self.assertEqual(self.client.get(f'/proofs/{proof.id}/image/').status_code,200)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/proofs/{proof.id}/image/').status_code,404)
    def test_admin_verify_once_and_cross_role_denied(self):
        from .models import TransferProof, Payment
        proof=TransferProof.objects.create(invoice=Invoice.objects.get(),guardian=self.guardian,reported_amount=100000,transfer_date=date(2026,10,27),image=b'x',image_type='png')
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(f'/proofs/{proof.id}/verify/').status_code,404)
        admin=get_user_model().objects.create_user(username='proof-admin',password='long-test-password')
        Membership.objects.create(user=admin,school=self.school,role='admin')
        self.client.force_login(admin)
        self.assertEqual(self.client.post(f'/proofs/{proof.id}/verify/').status_code,302)
        self.assertEqual(self.client.post(f'/proofs/{proof.id}/verify/').status_code,400)
        self.assertEqual(Payment.objects.count(),1)
    def test_invalid_photo_rejected(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from .models import TransferProof
        self.client.force_login(self.guardian)
        response=self.client.post('/invoices/1/proof/',{'amount':'100','transfer_date':'2026-10-27','image':SimpleUploadedFile('fake.png',b'not an image')})
        self.assertContains(response,'Foto tidak valid')
        self.assertEqual(TransferProof.objects.count(),0)

    def test_superadmin_can_manage_school_and_view_data(self):
        user = get_user_model().objects.create_superuser(username='root-user',email='root@example.test',password='long-test-password')
        self.client.force_login(user)
        self.assertContains(self.client.get('/dashboard/'),'ANAK SATU')
        self.assertEqual(self.client.get('/admin/portal/school/').status_code,200)
        self.assertEqual(self.client.get('/admin/portal/membership/').status_code,200)
    def test_staff_without_superuser_cannot_use_admin(self):
        staff = get_user_model().objects.create_user(username='staff-user',password='long-test-password',is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get('/admin/portal/membership/').status_code,302)

    def test_integration_status_only_superuser_never_displays_secret(self):
        from unittest.mock import patch
        root = get_user_model().objects.create_superuser(username='super-settings',email='root@example.test',password='long-test-password')
        with patch.dict('os.environ', {'SMTP_PASSWORD':'secret-value-for-test'}):
            self.client.force_login(root)
            response = self.client.get('/superadmin/integrations/')
            self.assertContains(response,'Midtrans')
            self.assertNotContains(response,'secret-value-for-test')
            self.client.force_login(self.guardian)
            self.assertEqual(self.client.get('/superadmin/integrations/').status_code,404)

    def test_student_crud_scoped_to_admin_school(self):
        User=get_user_model()
        admin=User.objects.create_user(username='student-admin',password='long-test-password')
        Membership.objects.create(user=admin,school=self.school,role='admin')
        outsider=Student.objects.create(school=self.other_school,nis='009',name='ANAK LUAR')
        self.client.force_login(admin)
        self.assertContains(self.client.get('/students/'),'ANAK SATU')
        self.assertNotContains(self.client.get('/students/'),'ANAK LUAR')
        self.assertEqual(self.client.get(f'/students/{outsider.pk}/edit/').status_code,404)
        self.assertEqual(self.client.post('/students/new/',{'school':self.other_school.pk,'nis':'002','name':'NOT ALLOWED','active':'on'}).status_code,200)
        self.assertFalse(Student.objects.filter(nis='002').exists())
        self.assertEqual(self.client.post('/students/new/',{'school':self.school.pk,'nis':'0002','name':'Anak baru','active':'on'}).status_code,302)
        self.assertTrue(Student.objects.filter(nis='0002').exists())
        self.assertEqual(self.client.post(f'/students/{self.student.pk}/deactivate/').status_code,302)
        self.student.refresh_from_db();self.assertFalse(self.student.active)
    def test_guardian_cannot_manage_students(self):
        self.client.force_login(self.guardian)
        self.assertEqual(self.client.get('/students/').status_code,404)
        self.assertEqual(self.client.get('/students/export.xlsx').status_code,404)
        self.assertEqual(self.client.post(f'/students/{self.student.pk}/deactivate/').status_code,404)
    def test_export_escapes_formulas_and_preserves_scope(self):
        from io import BytesIO
        from openpyxl import load_workbook
        admin=get_user_model().objects.create_user(username='export-admin',password='long-test-password')
        Membership.objects.create(user=admin,school=self.school,role='admin')
        Student.objects.create(school=self.school,nis='00009',name='=1+1')
        Student.objects.create(school=self.other_school,nis='00010',name='PRIVATE')
        self.client.force_login(admin)
        response=self.client.get('/students/export.xlsx')
        self.assertEqual(response.status_code,200)
        rows=list(load_workbook(BytesIO(response.content)).active.values)
        self.assertIn(('SHB','00009',"'=1+1",'Aktif'),rows)
        self.assertFalse(any('PRIVATE' in row for row in rows))
