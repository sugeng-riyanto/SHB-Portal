from io import BytesIO
from django import forms
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from .models import ActivityEvent, PaymentType, School
from .students import admin_school_ids, safe_cell

DEFAULT_TYPES = ('Monthly', 'ECA', 'Annual Fee', 'Stationery', 'Late Fee')

class PaymentTypeForm(forms.ModelForm):
    class Meta:
        model=PaymentType
        fields=('school','name','active')
    def __init__(self,*args,user,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['school'].queryset=School.objects.filter(id__in=admin_school_ids(user))

@login_required
def list_types(request):
    schools=admin_school_ids(request.user)
    if not schools.exists(): raise Http404
    items=PaymentType.objects.filter(school_id__in=schools).select_related('school').order_by('school__name','name')[:200]
    return render(request,'portal/payment_types.html',{'items':items,'schools':School.objects.filter(id__in=schools)})

@login_required
def edit_type(request,type_id=None):
    schools=admin_school_ids(request.user)
    if not schools.exists(): raise Http404
    item=get_object_or_404(PaymentType,pk=type_id,school_id__in=schools) if type_id else None
    old_school=item.school_id if item else None
    form=PaymentTypeForm(request.POST or None,instance=item,user=request.user)
    if request.method=='POST' and form.is_valid():
        if old_school and form.cleaned_data['school'].id != old_school:
            form.add_error('school','Changing schools is not allowed.')
        else:
            with transaction.atomic():
                obj=form.save();ActivityEvent.objects.create(school=obj.school,actor=request.user,action='payment_type_updated' if type_id else 'payment_type_created')
            return redirect('payment_types')
    return render(request,'portal/payment_type_form.html',{'form':form,'item':item})

@login_required
@require_POST
def deactivate_type(request,type_id):
    item=get_object_or_404(PaymentType,pk=type_id,school_id__in=admin_school_ids(request.user))
    with transaction.atomic():
        item.active=False;item.save(update_fields=['active'])
        ActivityEvent.objects.create(school=item.school,actor=request.user,action='payment_type_deactivated')
    return redirect('payment_types')

@login_required
@require_POST
def add_defaults(request):
    school=get_object_or_404(School,pk=request.POST.get('school'),pk__in=admin_school_ids(request.user))
    with transaction.atomic():
        for name in DEFAULT_TYPES: PaymentType.objects.get_or_create(school=school,name=name)
        ActivityEvent.objects.create(school=school,actor=request.user,action='payment_type_defaults_initialized')
    return redirect('payment_types')

@login_required
def export_types(request):
    schools=admin_school_ids(request.user)
    if not schools.exists(): raise Http404
    book=Workbook();sheet=book.active;sheet.title='Payment types';sheet.append(['School','Payment type','Status'])
    for item in PaymentType.objects.filter(school_id__in=schools).select_related('school').order_by('name').iterator():
        sheet.append([safe_cell(item.school.name),safe_cell(item.name),'Active' if item.active else 'Inactive'])
    stream=BytesIO();book.save(stream)
    response=HttpResponse(stream.getvalue(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition']='attachment; filename="payment-types.xlsx"';response['Cache-Control']='private, no-store'
    return response

@login_required
def activities(request):
    schools=admin_school_ids(request.user)
    if not schools.exists(): raise Http404
    events=ActivityEvent.objects.filter(school_id__in=schools).select_related('school','actor')[:200]
    return render(request,'portal/activities.html',{'events':events})
