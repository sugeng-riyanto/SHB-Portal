from io import BytesIO
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from .models import Membership, School, Student


def admin_school_ids(user):
    if not user.is_active:
        return School.objects.none().values_list('id', flat=True)
    if user.is_superuser:
        return School.objects.values_list('id', flat=True)
    return Membership.objects.filter(user=user, active=True, role=Membership.Role.ADMIN).values_list('school_id', flat=True)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('school', 'nis', 'name', 'active')
        labels = {'school':'Sekolah','nis':'NIS','name':'Nama murid','active':'Aktif'}
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['school'].queryset = School.objects.filter(id__in=admin_school_ids(user))
    def clean_nis(self):
        return self.cleaned_data['nis'].strip()

@login_required
def student_list(request):
    schools = admin_school_ids(request.user)
    if not schools.exists():
        raise Http404
    query = request.GET.get('q','').strip()[:100]
    students = Student.objects.filter(school_id__in=schools).select_related('school')
    if query:
        students = students.filter(Q(name__icontains=query) | Q(nis__icontains=query))
    return render(request,'portal/student_list.html',{'students':students.order_by('name')[:200], 'query':query})

@login_required
def student_edit(request, student_id=None):
    schools = admin_school_ids(request.user)
    if not schools.exists():
        raise Http404
    instance = get_object_or_404(Student, pk=student_id,school_id__in=schools) if student_id else None
    form = StudentForm(request.POST or None, instance=instance, user=request.user)
    if request.method == 'POST' and form.is_valid():
        if instance and form.cleaned_data['school'].id != instance.school_id:
            form.add_error('school','Pemindahan sekolah memerlukan alur khusus.')
        else:
            form.save()
            return redirect('student_list')
    return render(request,'portal/student_form.html',{'form':form,'student':instance})

@login_required
@require_POST
def student_deactivate(request, student_id):
    student = get_object_or_404(Student,pk=student_id,school_id__in=admin_school_ids(request.user))
    student.active = False
    student.save(update_fields=['active'])
    return redirect('student_list')

def safe_cell(value):
    value = str(value or '')
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value

@login_required
def student_export(request):
    schools=admin_school_ids(request.user)
    if not schools.exists():
        raise Http404
    query=request.GET.get('q','').strip()[:100]
    rows=Student.objects.filter(school_id__in=schools).select_related('school')
    if query:
        rows=rows.filter(Q(name__icontains=query)|Q(nis__icontains=query))
    book=Workbook();sheet=book.active;sheet.title='Murid';sheet.append(['Sekolah','NIS','Nama','Status'])
    for student in rows.order_by('name').iterator():
        sheet.append([safe_cell(student.school.name),safe_cell(student.nis),safe_cell(student.name),'Aktif' if student.active else 'Nonaktif'])
    out=BytesIO();book.save(out)
    response=HttpResponse(out.getvalue(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition']='attachment; filename="murid.xlsx"'
    response['Cache-Control']='private, no-store'
    return response
