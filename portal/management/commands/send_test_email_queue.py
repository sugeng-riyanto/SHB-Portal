"""Explicitly process a small allowlisted staging-only email queue."""
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError
from portal.models import Membership, Message

class Command(BaseCommand):
    help = 'Process a bounded batch of explicitly allowlisted staging test emails.'
    def add_arguments(self, parser):
        parser.add_argument('--limit',type=int,default=10)
    def handle(self,*args,**options):
        allowed={a.strip().casefold() for a in settings.SHB_EMAIL_TEST_RECIPIENTS if a.strip()}
        limit=options['limit']
        if settings.PRODUCTION or not settings.SHB_EMAIL_ENABLED or not allowed or not 1 <= limit <= 20:
            raise CommandError('Email queue requires staging, enabled email, an allowlist and limit 1–20.')
        ids=list(Message.objects.filter(email_status=Message.Delivery.PENDING).exclude(email_destination='').order_by('pk').values_list('pk',flat=True)[:limit])
        accepted=0;blocked=0;unknown=0
        for pk in ids:
            if not Message.objects.filter(pk=pk,email_status=Message.Delivery.PENDING).update(email_status=Message.Delivery.SENDING): continue
            item=Message.objects.select_related('recipient').get(pk=pk)
            current=item.recipient.email.strip()
            active=Membership.objects.filter(user=item.recipient,school=item.school,role=Membership.Role.GUARDIAN,active=True).exists()
            if not item.recipient.is_active or not active or current != item.email_destination or current.casefold() not in allowed:
                item.email_status=Message.Delivery.FAILED;item.save(update_fields=['email_status']);blocked+=1;continue
            try:
                from portal.smtp_config import smtp_connection
                connection, sender = smtp_connection()
                result=EmailMessage(item.subject,item.body,sender,[item.email_destination],connection=connection).send(fail_silently=False)
                if result != 1: raise RuntimeError('No SMTP acceptance')
                item.email_status=Message.Delivery.SENT;accepted+=1
            except Exception:
                # A failed SMTP call may have been accepted; never retry automatically.
                item.email_status=Message.Delivery.UNKNOWN;unknown+=1
            item.save(update_fields=['email_status'])
        self.stdout.write(f'Accepted: {accepted}; blocked: {blocked}; needs review: {unknown}.')
