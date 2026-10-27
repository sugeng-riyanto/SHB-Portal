from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

class School(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self): return self.name

class Membership(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin sekolah'
        PRINCIPAL = 'principal', 'Kepala sekolah'
        FOUNDATION = 'foundation', 'Yayasan'
        TEACHER = 'teacher', 'Wali kelas'
        GUARDIAN = 'guardian', 'Orang tua / wali'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    school = models.ForeignKey(School, on_delete=models.PROTECT)
    role = models.CharField(max_length=20, choices=Role.choices)
    active = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'school', 'role'], name='unique_membership')]

class AcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT)
    label = models.CharField(max_length=20)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['school','label'],name='unique_year_per_school')]

class Classroom(models.Model):
    year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT)
    name = models.CharField(max_length=20)
    teachers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='assigned_classes')
    class Meta:
        constraints = [models.UniqueConstraint(fields=['year','name'], name='unique_class_per_year')]
    def __str__(self): return self.name

class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT)
    nis = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    guardians = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='linked_students', blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['school','nis'],name='unique_nis_per_school')]
    def __str__(self): return self.name

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    classroom = models.ForeignKey(Classroom, on_delete=models.PROTECT)
    def clean(self):
        if self.student_id and self.classroom_id and self.student.school_id != self.classroom.year.school_id:
            raise ValidationError('Student and classroom must belong to the same school.')

class Invoice(models.Model):
    enrollment = models.ForeignKey(Enrollment,on_delete=models.PROTECT)
    reference = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200)
    amount = models.PositiveBigIntegerField()
    fine = models.PositiveBigIntegerField(default=0)
    due_date = models.DateField()
    virtual_account = models.CharField(max_length=64, blank=True)
    cancelled = models.BooleanField(default=False)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(amount__gte=0,fine__gte=0), name='invoice_nonnegative')]

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice,on_delete=models.PROTECT, related_name='payments')
    amount = models.PositiveBigIntegerField()
    verified = models.BooleanField(default=False)
    class Meta:
        constraints = [models.CheckConstraint(condition=Q(amount__gt=0),name='payment_positive')]
