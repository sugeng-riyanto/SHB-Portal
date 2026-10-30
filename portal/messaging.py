"""Individual, explicitly requested notifications. No automatic retries."""
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.utils.html import escape
from .models import Membership, Message, School
from .students import admin_school_ids

class MessageForm(forms.Form):
    school=forms.ModelChoiceField(queryset=School.objects.none(),label='Sekolah')
    recipient=forms.ModelChoiceField(queryset=get_user_model().objects.none(),label='Wali penerima')
    subject=forms.CharField(max_length=160,label='Subjek')
    body=forms.CharField(max_length=5000,widget=forms.Textarea,label='Pesan')
    def __init__(self,*args,user,**kwargs):
        super().__init__(*args,**kwargs)
        schools=School.objects.filter(id__in=admin_school_ids(user))
        self.fields['school'].queryset=schools
        self.fields['recipient'].queryset=get_user_model().objects.filter(is_active=True,membership__school__in=schools,membership__role=Membership.Role.GUARDIAN,membership__active=True).distinct()
    def clean(self):
        values=super().clean();school=values.get('school');recipient=values.get('recipient')
        if school and recipient and not Membership.objects.filter(school=school,user=recipient,role=Membership.Role.GUARDIAN,active=True).exists():
            raise forms.ValidationError('Wali tidak terdaftar pada sekolah yang dipilih.')
        if recipient and not recipient.email:
            self.add_error('recipient','Wali belum memiliki email.')
        return values

@login_required
def compose(request):
    if not admin_school_ids(request.user).exists(): raise Http404
    form=MessageForm(request.POST or None,user=request.user)
    if request.method=='POST' and form.is_valid():
        values=form.cleaned_data
        message=Message.objects.create(school=values['school'],sender=request.user,recipient=values['recipient'],subject=values['subject'],body=values['body'])
        # No automatic retry: failure can be ambiguous after SMTP acceptance.
        try:
            if not getattr(settings,'SHB_EMAIL_ENABLED',False):
                raise RuntimeError('Email disabled')
            from .smtp_config import smtp_connection
            connection, sender = smtp_connection()
            email=EmailMultiAlternatives(message.subject,message.body,sender,[message.recipient.email],connection=connection)
            email.attach_alternative('<p>'+escape(message.body).replace('\n','<br>')+'</p>','text/html')
            if email.send(fail_silently=False) != 1:
                raise RuntimeError('Not accepted')
            message.email_status=Message.Delivery.SENT
        except Exception:
            message.email_status=Message.Delivery.FAILED
        message.save(update_fields=['email_status'])
        return redirect('message_history')
    return render(request,'portal/message_compose.html',{'form':form})

@login_required
def history(request):
    schools=admin_school_ids(request.user)
    if not schools.exists(): raise Http404
    from django.db.models import Count, Q
    query=request.GET.get('q','').strip()[:160]
    status=request.GET.get('status','')
    school=request.GET.get('school','')
    group=request.GET.get('group','')
    messages=Message.objects.filter(school_id__in=schools).select_related('recipient','school')
    if query: messages=messages.filter(Q(recipient__email__icontains=query)|Q(subject__icontains=query))
    if status in Message.Delivery.values: messages=messages.filter(email_status=status)
    else: status=''
    if school.isdigit() and School.objects.filter(pk=int(school),id__in=schools).exists(): messages=messages.filter(school_id=int(school))
    else: school=''
    if group not in ('status','school'): group=''
    groups=[]
    if group == 'status':
        labels=dict(Message.Delivery.choices)
        groups=[{'label':labels.get(row['email_status'], row['email_status']), 'count':row['count']} for row in messages.values('email_status').annotate(count=Count('id')).order_by('email_status')]
    elif group == 'school':
        groups=[{'label':row['school__name'], 'count':row['count']} for row in messages.values('school_id','school__name').annotate(count=Count('id')).order_by('school__name')]
    from django.core.paginator import Paginator
    page=Paginator(messages.order_by('-created_at','-pk'),100).get_page(request.GET.get('page'))
    return render(request,'portal/message_history.html',{'messages':page, 'page':page, 'groups':groups, 'q':query, 'status':status, 'school':school, 'group':group, 'schools':School.objects.filter(id__in=schools), 'statuses':Message.Delivery.choices})

@login_required
def inbox(request):
    active_schools=Membership.objects.filter(user=request.user,role=Membership.Role.GUARDIAN,active=True).values_list('school_id',flat=True)
    messages=Message.objects.filter(recipient=request.user,school_id__in=active_schools).order_by('-created_at')[:100]
    return render(request,'portal/inbox.html',{'messages':messages})

class BulkInboxForm(forms.Form):
    school=forms.ModelChoiceField(queryset=School.objects.none(),label='Sekolah')
    audience=forms.ChoiceField(choices=[('all','Semua wali'),('class','Satu kelas'),('selected','Wali terpilih')],label='Penerima')
    classroom=forms.ModelChoiceField(queryset=None,required=False,label='Kelas')
    recipients=forms.ModelMultipleChoiceField(queryset=get_user_model().objects.none(),required=False,label='Wali terpilih',widget=forms.SelectMultiple(attrs={'size':6}))
    subject=forms.CharField(max_length=160,label='Subjek')
    body=forms.CharField(max_length=5000,label='Pesan',widget=forms.Textarea(attrs={'rows':6}))
    email_test=forms.BooleanField(required=False,label='Antrekan email uji ke alamat yang diizinkan server')
    def __init__(self,*args,user,**kwargs):
        from .models import Classroom
        super().__init__(*args,**kwargs)
        schools=School.objects.filter(pk__in=admin_school_ids(user))
        self.fields['school'].queryset=schools
        self.fields['classroom'].queryset=Classroom.objects.filter(year__school__in=schools).select_related('year')
        self.fields['recipients'].queryset=get_user_model().objects.filter(is_active=True,membership__school__in=schools,membership__active=True,membership__role=Membership.Role.GUARDIAN).distinct().order_by('username')
    def clean(self):
        values=super().clean(); school=values.get('school'); audience=values.get('audience'); classroom=values.get('classroom')
        if audience=='class' and (not classroom or not school or classroom.year.school_id != school.pk):
            self.add_error('classroom','Pilih kelas pada sekolah yang dipilih.')
        if audience=='selected' and not values.get('recipients'):
            self.add_error('recipients','Pilih setidaknya satu wali.')
        return values

def eligible_guardians(school, audience, classroom_id=None):
    guardians=get_user_model().objects.filter(is_active=True,membership__school=school,membership__active=True,membership__role=Membership.Role.GUARDIAN)
    if audience=='class':
        guardians=guardians.filter(linked_students__school=school,linked_students__active=True,linked_students__enrollment__classroom_id=classroom_id,linked_students__enrollment__classroom__year__school=school)
    return guardians.distinct().order_by('pk')

@login_required
def bulk_inbox_preview(request):
    import secrets
    from django.utils import timezone
    if not admin_school_ids(request.user).exists(): raise Http404
    form=BulkInboxForm(request.POST or None,user=request.user)
    context={'form':form}
    if request.method=='POST':
        request.session.pop('bulk_inbox_preview',None)
        if form.is_valid():
            values=form.cleaned_data; school=values['school']; audience=values['audience']; classroom=values['classroom']
            eligible=eligible_guardians(school,audience,classroom.pk if classroom else None)
            if audience=='selected':
                requested=set(values['recipients'].values_list('pk',flat=True))
                eligible=eligible.filter(pk__in=requested)
                if set(eligible.values_list('pk',flat=True)) != requested:
                    form.add_error('recipients','Ada wali di luar sekolah yang dipilih.')
                    return render(request,'portal/bulk_inbox.html',context)
            people=list(eligible[:201])
            if not people or len(people)>200:
                form.add_error(None,'Pilih antara 1 dan 200 wali.')
            elif values['email_test'] and not test_email_recipients_valid(people):
                form.add_error(None,'Email uji belum aktif, alamat tidak valid atau tidak ada dalam daftar izin server.')
            else:
                token=secrets.token_urlsafe(32)
                email_addresses={str(p.pk):p.email.strip() for p in people} if values['email_test'] else {}
                request.session['bulk_inbox_preview']={'token':token,'school':school.pk,'audience':audience,'classroom':classroom.pk if classroom else None,'recipients':[p.pk for p in people],'emails':email_addresses,'subject':values['subject'],'body':values['body'],'created':timezone.now().isoformat()}
                context.update(preview=people,token=token,subject=values['subject'],body=values['body'],school=school,email_test=values['email_test'])
    return render(request,'portal/bulk_inbox.html',context)

def test_email_recipients_valid(people):
    from django.core.exceptions import ValidationError
    from django.core.validators import validate_email
    allowed={address.strip().casefold() for address in getattr(settings,'SHB_EMAIL_TEST_RECIPIENTS',[]) if address.strip()}
    if settings.PRODUCTION or not getattr(settings,'SHB_EMAIL_ENABLED',False) or not allowed: return False
    for person in people:
        address=person.email.strip()
        try: validate_email(address)
        except ValidationError: return False
        if address.casefold() not in allowed: return False
    return True

@login_required
@require_POST
def bulk_inbox_confirm(request):
    import hashlib, secrets
    from datetime import datetime, timedelta
    from django.db import IntegrityError, transaction
    from django.http import HttpResponseBadRequest
    from django.utils import timezone
    from .models import MessageBatch, ActivityEvent, Classroom
    batch=request.session.get('bulk_inbox_preview')
    if not batch or not secrets.compare_digest(str(request.POST.get('token','')),batch['token']):
        return HttpResponseBadRequest('Preview tidak tersedia atau sudah digunakan.')
    try:
        if timezone.now()-datetime.fromisoformat(batch['created']) > timedelta(minutes=15):
            return HttpResponseBadRequest('Preview kedaluwarsa; mulai ulang.')
    except (ValueError, TypeError): return HttpResponseBadRequest('Preview tidak valid.')
    school=School.objects.filter(pk=batch['school'],pk__in=admin_school_ids(request.user)).first()
    if not school: raise Http404
    if batch['audience']=='class' and not Classroom.objects.filter(pk=batch['classroom'],year__school=school).exists():
        return HttpResponseBadRequest('Kelas tidak tersedia; mulai ulang.')
    wanted=set(batch['recipients'])
    try:
        with transaction.atomic():
            School.objects.select_for_update().get(pk=school.pk)
            current=set(eligible_guardians(school,batch['audience'],batch['classroom']).filter(pk__in=wanted).values_list('pk',flat=True))
            if current!=wanted: return HttpResponseBadRequest('Akses penerima berubah; periksa ulang.')
            email_addresses=batch.get('emails',{})
            if email_addresses:
                people=list(eligible_guardians(school,batch['audience'],batch['classroom']).filter(pk__in=wanted))
                if not test_email_recipients_valid(people) or any(email_addresses.get(str(p.pk)) != p.email.strip() for p in people):
                    return HttpResponseBadRequest('Alamat atau izin email berubah; periksa ulang.')
            MessageBatch.objects.create(token_hash=hashlib.sha256(batch['token'].encode()).hexdigest(),school=school,sender=request.user)
            Message.objects.bulk_create([Message(school=school,sender=request.user,recipient_id=pk,subject=batch['subject'],body=batch['body'],email_status=Message.Delivery.PENDING if email_addresses else Message.Delivery.NOT_REQUESTED,email_destination=email_addresses.get(str(pk),'')) for pk in sorted(wanted)])
            ActivityEvent.objects.create(school=school,actor=request.user,action='bulk_inbox_sent')
    except IntegrityError:
        return HttpResponseBadRequest('Pesan sudah dikirim atau data berubah.')
    request.session.pop('bulk_inbox_preview',None)
    return redirect('message_history')
