"""Scoped SMTP configuration: explicit Gmail TLS or fail closed."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import get_connection
from django.core.validators import validate_email
from .integrations import cipher, decrypt
from .models import IntegrationConfig

class SMTPConfigurationError(ValueError):
    pass

def smtp_connection(use_dashboard=True):
    config=IntegrationConfig.objects.filter(provider='smtp').first() if use_dashboard else None
    if config is None:
        return get_connection(),settings.DEFAULT_FROM_EMAIL
    if not config.active:
        raise SMTPConfigurationError('SMTP dashboard nonaktif.')
    key=cipher()
    if key is None: raise SMTPConfigurationError('Kunci enkripsi tidak tersedia.')
    try:
        secret=decrypt(config,key)
        public=config.public_config
        host=str(public.get('host','')).strip().lower()
        port=str(public.get('port','')).strip()
        username=str(public.get('username','')).strip()
        sender=str(public.get('from_email','')).strip()
        password=secret.get('app_password','')
        if host != 'smtp.gmail.com' or port != '587' or not isinstance(password,str) or not password:
            raise SMTPConfigurationError('Gunakan Gmail SMTP port 587, TLS, dan App Password.')
        validate_email(username);validate_email(sender)
        return get_connection(host=host,port=587,username=username,password=password,use_tls=True,use_ssl=False,timeout=15),sender
    except (ValidationError, ValueError, TypeError, AttributeError):
        raise SMTPConfigurationError('Konfigurasi Gmail belum valid atau kunci enkripsi tidak cocok.') from None
