from io import BytesIO
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from .models import BankAccount, Membership, School
from .students import safe_cell


def principal_school_ids(user):
    if not user.is_active:
        return School.objects.none().values_list('id', flat=True)
    if user.is_superuser:
        return School.objects.values_list('id', flat=True)
    return Membership.objects.filter(user=user, active=True, role=Membership.Role.PRINCIPAL).values_list('school_id', flat=True)

class BankForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ('school', 'bank_name', 'account_name', 'account_number', 'active')
        labels = {'school':'Sekolah', 'bank_name':'Nama bank', 'account_name':'Nama pemilik rekening', 'account_number':'Nomor rekening', 'active':'Aktif'}
    def __init__(self,*args,user,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['school'].queryset=School.objects.filter(id__in=principal_school_ids(user))
    def clean_account_number(self):
        value=self.cleaned_data['account_number'].strip()
        if not value.isdigit():
            raise forms.ValidationError('Nomor rekening hanya boleh berisi angka.')
        return value

@login_required
def bank_list(request):
    schools=principal_school_ids(request.user)
    if not schools.exists(): raise Http404
    accounts=BankAccount.objects.filter(school_id__in=schools).select_related('school').order_by('bank_name')[:200]
    return render(request,'portal/bank_list.html',{'accounts':accounts})

@login_required
def bank_edit(request,bank_id=None):
    schools=principal_school_ids(request.user)
    if not schools.exists(): raise Http404
    instance=get_object_or_404(BankAccount,pk=bank_id,school_id__in=schools) if bank_id else None
    form=BankForm(request.POST or None,instance=instance,user=request.user)
    if request.method=='POST' and form.is_valid():
        if instance and instance.school_id != form.cleaned_data['school'].id:
            form.add_error('school','Pemindahan sekolah tidak diperbolehkan.')
        else:
            form.save();return redirect('bank_list')
    return render(request,'portal/bank_form.html',{'form':form,'account':instance})

@login_required
@require_POST
def bank_deactivate(request,bank_id):
    account=get_object_or_404(BankAccount,pk=bank_id,school_id__in=principal_school_ids(request.user))
    account.active=False;account.save(update_fields=['active'])
    return redirect('bank_list')

@login_required
def bank_export(request):
    schools=principal_school_ids(request.user)
    if not schools.exists(): raise Http404
    book=Workbook();sheet=book.active;sheet.title='Rekening';sheet.append(['Sekolah','Bank','Nama pemilik','Nomor rekening','Status'])
    for account in BankAccount.objects.filter(school_id__in=schools).select_related('school').order_by('bank_name').iterator():
        sheet.append([safe_cell(account.school.name),safe_cell(account.bank_name),safe_cell(account.account_name),safe_cell(account.account_number),'Aktif' if account.active else 'Nonaktif'])
    out=BytesIO();book.save(out)
    response=HttpResponse(out.getvalue(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition']='attachment; filename="rekening-sekolah.xlsx"';response['Cache-Control']='private, no-store'
    return response
