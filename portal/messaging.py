"""Individual, explicitly requested notifications. No automatic retries."""
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import Http404
from django.shortcuts import redirect, render
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
            email=EmailMultiAlternatives(message.subject,message.body,settings.DEFAULT_FROM_EMAIL,[message.recipient.email])
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
    messages=Message.objects.filter(school_id__in=schools).select_related('recipient','school').order_by('-created_at')[:100]
    return render(request,'portal/message_history.html',{'messages':messages})

@login_required
def inbox(request):
    active_schools=Membership.objects.filter(user=request.user,role=Membership.Role.GUARDIAN,active=True).values_list('school_id',flat=True)
    messages=Message.objects.filter(recipient=request.user,school_id__in=active_schools).order_by('-created_at')[:100]
    return render(request,'portal/inbox.html',{'messages':messages})
