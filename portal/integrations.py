"""Super-admin integration configuration, encrypted at rest.

Settings are stored for later integration; they are not yet applied to services.
"""
import json
import os
from cryptography.fernet import Fernet, InvalidToken
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import IntegrationConfig

SPECS = {
    'supabase': {'public': ('project_url',), 'secret': ('publishable_key',)},
    'smtp': {'public': ('host','port','username','from_email'), 'secret': ('app_password',)},
    'midtrans': {'public': ('mode','client_key'), 'secret': ('server_key',)},
}

def cipher():
    key=os.environ.get('SHB_INTEGRATION_ENCRYPTION_KEY','')
    try:
        return Fernet(key.encode('ascii'))
    except (ValueError, TypeError, UnicodeEncodeError):
        return None

def check_superuser(user):
    if not user.is_active or not user.is_superuser: raise Http404

def decrypt(config, fernet):
    if not config or not config.encrypted_secrets: return {}
    try:
        value=json.loads(fernet.decrypt(bytes(config.encrypted_secrets)))
        if not isinstance(value,dict): raise ValueError
        return value
    except (InvalidToken, ValueError, TypeError):
        raise ValueError('Kunci enkripsi tidak cocok atau data rusak.') from None

class ConfigForm(forms.Form):
    active=forms.BooleanField(label='Aktif',required=False)
    def __init__(self,*args,provider,**kwargs):
        super().__init__(*args,**kwargs)
        spec=SPECS[provider]
        for name in spec['public']:
            self.fields[name]=forms.CharField(label=name.replace('_',' ').title(),max_length=300,required=False)
        for name in spec['secret']:
            self.fields[name]=forms.CharField(label=name.replace('_',' ').title(),max_length=2048,required=False,widget=forms.PasswordInput(render_value=False),help_text='Kosongkan untuk mempertahankan nilai yang sudah disimpan.')
    def clean_project_url(self):
        value=self.cleaned_data['project_url'].strip()
        if value:
            forms.URLField().clean(value)
            if not value.startswith('https://'): raise forms.ValidationError('Gunakan URL HTTPS.')
        return value
    def clean_port(self):
        value=self.cleaned_data['port'].strip()
        if value and (not value.isdigit() or not 1 <= int(value) <= 65535): raise forms.ValidationError('Port tidak valid.')
        return value
    def clean_mode(self):
        value=self.cleaned_data['mode'].strip().lower()
        if value and value not in ('sandbox','production'): raise forms.ValidationError('Isi sandbox atau production.')
        return value

@login_required
def index(request):
    check_superuser(request.user)
    items={x.provider:x for x in IntegrationConfig.objects.all()}
    rows=[{'key':p,'label':label,'item':items.get(p)} for p,label in IntegrationConfig.Provider.choices]
    response=render(request,'portal/integrations.html',{'integrations':rows,'key_ready':cipher() is not None})
    response['Cache-Control']='private, no-store'
    return response

@login_required
def edit(request,provider):
    check_superuser(request.user)
    if provider not in SPECS: raise Http404
    item=IntegrationConfig.objects.filter(provider=provider).first()
    fernet=cipher()
    initial=dict(item.public_config) if item else {}
    initial['active']=item.active if item else False
    form=ConfigForm(request.POST or None,provider=provider,initial=initial)
    error=None
    if request.method=='POST' and form.is_valid():
        if fernet is None:
            error='Kunci enkripsi server belum dikonfigurasi; pengaturan belum disimpan.'
        else:
            try:
                secret=decrypt(item,fernet)
                for key in SPECS[provider]['secret']:
                    value=form.cleaned_data[key]
                    if value: secret[key]=value
                public={key:form.cleaned_data[key] for key in SPECS[provider]['public']}
                token=fernet.encrypt(json.dumps(secret).encode())
                IntegrationConfig.objects.update_or_create(provider=provider,defaults={'public_config':public,'encrypted_secrets':token,'active':form.cleaned_data['active']})
                return redirect('integration_settings')
            except ValueError as exc:
                error=str(exc)
    response=render(request,'portal/integration_form.html',{'form':form,'provider':provider,'error':error,'key_ready':fernet is not None})
    response['Cache-Control']='private, no-store'
    return response

@login_required
@require_POST
def remove(request,provider):
    check_superuser(request.user)
    if provider not in SPECS: raise Http404
    config=get_object_or_404(IntegrationConfig,provider=provider)
    config.delete()
    return redirect('integration_settings')

@login_required
def reveal(request,provider):
    """Re-authenticate before showing stored secrets to an active superuser."""
    import logging
    from django.views.decorators.debug import sensitive_post_parameters
    from django.contrib.auth import authenticate
    from django.core.cache import cache
    check_superuser(request.user)
    if provider not in SPECS: raise Http404
    config=get_object_or_404(IntegrationConfig,provider=provider)
    error=None
    secrets=None
    if request.method=='POST':
        # Authentication backends apply their usual password checking; do not log input.
        password=request.POST.get('password','')
        limit_key=f'shb:reveal:attempts:{request.user.pk}'
        try:
            cache.add(limit_key, 0, timeout=900)
            attempts=cache.incr(limit_key)
        except Exception:
            attempts=6  # Fail closed if the rate-limit store is unavailable.
        user=authenticate(request,username=request.user.get_username(),password=password) if attempts <= 5 else None
        if attempts > 5:
            error='Terlalu banyak percobaan. Coba lagi setelah 15 menit.'
        elif user is None or user.pk != request.user.pk or not user.is_active or not user.is_superuser:
            error='Password tidak valid.'
        elif cipher() is None:
            error='Kunci enkripsi server belum tersedia.'
        else:
            try:
                secrets=decrypt(config,cipher())
                cache.delete(limit_key)
                logging.getLogger('shb.security').warning('Integration secret viewed: user_id=%s provider=%s',request.user.pk,provider)
            except ValueError as exc:
                error=str(exc)
    response=render(request,'portal/integration_reveal.html',{'provider':provider,'error':error,'secrets':secrets})
    response['Cache-Control']='private, no-store, max-age=0'
    response['Pragma']='no-cache'
    return response

# Ensure password input is redacted from Django error reports.
from django.views.decorators.debug import sensitive_post_parameters
reveal = sensitive_post_parameters('password')(reveal)
