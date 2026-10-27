"""School-scoped announcements with principal approval, not legal signatures."""
import uuid
from io import BytesIO
from django import forms
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
import qrcode
from .models import Membership, School, SchoolAnnouncement
from .students import admin_school_ids
from .banks import principal_school_ids

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model=SchoolAnnouncement
        fields=('school','title','body','event_date','pdf_url')
        labels={'school':'School','title':'Title','body':'Announcement paragraphs','event_date':'Activity date','pdf_url':'PDF link (HTTPS, optional)'}
        widgets={'body':forms.Textarea(attrs={'rows':8}),'event_date':forms.DateInput(attrs={'type':'date'})}
    def __init__(self,*args,user,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['school'].queryset=School.objects.filter(id__in=admin_school_ids(user))
    def clean_pdf_url(self):
        url=self.cleaned_data['pdf_url']
        if url and not url.lower().startswith('https://'):
            raise forms.ValidationError('Use an HTTPS link.')
        return url

@login_required
def list_announcements(request):
    from django.db.models import Q
    allowed=Q(school_id__in=admin_school_ids(request.user)) | Q(school_id__in=principal_school_ids(request.user))
    items=list(SchoolAnnouncement.objects.filter(allowed).select_related('school','approved_by').order_by('-created_at')[:200])
    admin_ids=set(admin_school_ids(request.user))
    principal_ids=set(Membership.objects.filter(user=request.user,school_id__in=principal_school_ids(request.user),role=Membership.Role.PRINCIPAL,active=True).values_list('school_id',flat=True))
    for item in items:
        item.may_edit=item.school_id in admin_ids and item.status == SchoolAnnouncement.Status.DRAFT
        item.may_approve=item.school_id in principal_ids and item.status == SchoolAnnouncement.Status.SUBMITTED
    if not admin_school_ids(request.user).exists() and not principal_school_ids(request.user).exists(): raise Http404
    return render(request,'portal/announcement_list.html',{'items':items})

@login_required
def edit(request,announcement_id=None):
    schools=admin_school_ids(request.user)
    if not schools.exists(): raise Http404
    item=get_object_or_404(SchoolAnnouncement,pk=announcement_id,school_id__in=schools) if announcement_id else None
    if item and item.status != SchoolAnnouncement.Status.DRAFT: return HttpResponseBadRequest('Only drafts can be edited.')
    original_school=item.school_id if item else None
    form=AnnouncementForm(request.POST or None,instance=item,user=request.user)
    if request.method=='POST' and form.is_valid():
        if original_school and form.cleaned_data['school'].pk != original_school:
            form.add_error('school','Changing schools is not allowed.')
        else:
            with transaction.atomic():
                if item:
                    obj=get_object_or_404(SchoolAnnouncement.objects.select_for_update(),pk=announcement_id,school_id__in=admin_school_ids(request.user))
                    if obj.status != SchoolAnnouncement.Status.DRAFT:
                        return HttpResponseBadRequest('Only drafts can be edited.')
                    for name in ('title','body','event_date','pdf_url'):
                        setattr(obj,name,form.cleaned_data[name])
                    obj.save(update_fields=['title','body','event_date','pdf_url'])
                else:
                    obj=form.save(commit=False);obj.created_by=request.user;obj.save()
            return redirect('announcement_list')
    return render(request,'portal/announcement_form.html',{'form':form,'item':item})

@login_required
@require_POST
def submit(request,announcement_id):
    with transaction.atomic():
        item=get_object_or_404(SchoolAnnouncement.objects.select_for_update(),pk=announcement_id,school_id__in=admin_school_ids(request.user))
        if item.status != SchoolAnnouncement.Status.DRAFT: return HttpResponseBadRequest('Only drafts can be submitted.')
        item.status=SchoolAnnouncement.Status.SUBMITTED;item.save(update_fields=['status'])
    return redirect('announcement_list')

@login_required
@require_POST
def remove(request,announcement_id):
    with transaction.atomic():
        item=get_object_or_404(SchoolAnnouncement.objects.select_for_update(),pk=announcement_id,school_id__in=admin_school_ids(request.user))
        if item.status != SchoolAnnouncement.Status.DRAFT: return HttpResponseBadRequest('Only drafts can be deleted.')
        item.delete()
    return redirect('announcement_list')

@login_required
@require_POST
def approve(request,announcement_id):
    # Approval requires an actual principal membership, not merely superuser status.
    with transaction.atomic():
        item=get_object_or_404(SchoolAnnouncement.objects.select_for_update(),pk=announcement_id)
        if not Membership.objects.filter(user=request.user,school=item.school,role=Membership.Role.PRINCIPAL,active=True).exists(): raise Http404
        if item.status != SchoolAnnouncement.Status.SUBMITTED: return HttpResponseBadRequest('Announcement is not awaiting approval.')
        item.status=SchoolAnnouncement.Status.APPROVED;item.approved_by=request.user;item.approved_at=timezone.now();item.approval_reference=uuid.uuid4()
        item.save(update_fields=['status','approved_by','approved_at','approval_reference'])
    return redirect('announcement_list')

@login_required
def verify(request,reference):
    from django.db.models import Q
    allowed=Q(school_id__in=admin_school_ids(request.user)) | Q(school_id__in=principal_school_ids(request.user))
    item=get_object_or_404(SchoolAnnouncement.objects.select_related('school','approved_by').filter(allowed),approval_reference=reference,status=SchoolAnnouncement.Status.APPROVED)
    response=render(request,'portal/announcement_verify.html',{'item':item})
    response['Cache-Control']='private, no-store';return response

@login_required
def qr(request,reference):
    from django.db.models import Q
    allowed=Q(school_id__in=admin_school_ids(request.user)) | Q(school_id__in=principal_school_ids(request.user))
    get_object_or_404(SchoolAnnouncement.objects.filter(allowed),approval_reference=reference,status=SchoolAnnouncement.Status.APPROVED)
    url=request.build_absolute_uri(reverse('announcement_verify',args=[reference]))
    image=qrcode.make(url);out=BytesIO();image.save(out,format='PNG')
    response=HttpResponse(out.getvalue(),content_type='image/png');response['Cache-Control']='private, no-store';response['X-Content-Type-Options']='nosniff';return response
