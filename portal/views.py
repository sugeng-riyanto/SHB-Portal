from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from .access import aggregate_invoices, scoped_invoices
from .models import Membership

def public_information():
    import os
    from urllib.parse import urlsplit
    from django.utils import timezone
    from .models import SchoolUpdate
    social=[]
    for label, key in [('Instagram','SHB_INSTAGRAM_URL'),('Facebook','SHB_FACEBOOK_URL'),('YouTube','SHB_YOUTUBE_URL')]:
        url=os.environ.get(key,'').strip()
        parsed=urlsplit(url)
        if parsed.scheme == 'https' and parsed.netloc and not parsed.username and not parsed.password:
            social.append({'label':label,'url':url})
    updates=SchoolUpdate.objects.filter(published=True,published_at__isnull=False,published_at__lte=timezone.now())
    return {'school_updates':updates[:6], 'social_links':social}

def home(request):
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard')
    return render(request, 'portal/home.html', public_information())

def school_news(request):
    return render(request, 'portal/school_news.html', public_information())

@login_required
def dashboard(request):
    memberships = Membership.objects.filter(user=request.user, active=True).select_related('school')
    invoices = scoped_invoices(request.user).select_related('enrollment__student','enrollment__classroom')[:100]
    summary = aggregate_invoices(request.user).aggregate(count=Count('id'), total=Sum('amount'))
    return render(request, 'portal/dashboard.html', {'memberships': memberships, 'invoices': invoices, 'summary': summary})

from django.http import HttpResponse, HttpResponseForbidden
from .imports import ImportErrorDetail, preview_xlsx, template_bytes, MAX_BYTES

def admin_only(user):
    return bool(user.is_active and user.is_superuser) or Membership.objects.filter(user=user, role=Membership.Role.ADMIN, active=True).exists()

@login_required
def xlsx_template(request):
    if not admin_only(request.user):
        return HttpResponseForbidden('Tidak diizinkan.')
    response = HttpResponse(template_bytes(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="template-tagihan.xlsx"'
    return response

@login_required
def import_preview(request):
    if not admin_only(request.user):
        return HttpResponseForbidden('Tidak diizinkan.')
    context = {}
    if request.method == 'POST':
        uploaded = request.FILES.get('file')
        if not uploaded or uploaded.size > MAX_BYTES or not uploaded.name.lower().endswith('.xlsx'):
            context['error'] = 'Pilih file XLSX maksimal 2 MB.'
        else:
            try:
                context['rows'] = preview_xlsx(uploaded.read(MAX_BYTES + 1))
                context['previewed'] = True
            except ImportErrorDetail as exc:
                context['error'] = str(exc)
    return render(request, 'portal/import_preview.html', context)

from datetime import date
from django.db import transaction
from django.db.models import Sum
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .access import scoped_invoices
from .models import Invoice, Payment, TransferProof
from .proofs import accessible_proofs, validate_image

@login_required
def proofs_list(request):
    proofs = list(accessible_proofs(request.user).select_related('invoice__enrollment__student')[:100])
    admin_schools = set(Membership.objects.filter(user=request.user, active=True, role=Membership.Role.ADMIN).values_list('school_id', flat=True))
    if request.user.is_active and request.user.is_superuser:
        from .models import School
        admin_schools.update(School.objects.values_list('id', flat=True))
    for proof in proofs:
        proof.may_verify = proof.invoice.enrollment.student.school_id in admin_schools
        proof.may_edit = proof.guardian_id == request.user.id and proof.status == TransferProof.Status.PENDING
    return render(request, 'portal/proofs.html', {'proofs': proofs})

@login_required
def proof_upload(request, invoice_id):
    invoice = get_object_or_404(scoped_invoices(request.user).filter(
        enrollment__student__guardians=request.user,
        enrollment__student__school__membership__user=request.user,
        enrollment__student__school__membership__role=Membership.Role.GUARDIAN,
        enrollment__student__school__membership__active=True).distinct(), pk=invoice_id)
    context = {'invoice': invoice}
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', ''))
            transfer_date = date.fromisoformat(request.POST.get('transfer_date', ''))
            if amount <= 0 or invoice.cancelled:
                raise ValueError('Nominal atau tagihan tidak valid.')
            image = request.FILES.get('image')
            if not image:
                raise ValueError('Pilih foto bukti transfer.')
            data, image_type = validate_image(image)
            TransferProof.objects.create(invoice=invoice, guardian=request.user, reported_amount=amount,
                transfer_date=transfer_date, image=data, image_type=image_type)
            return redirect('proofs_list')
        except (ValueError, OverflowError) as exc:
            context['error'] = str(exc) or 'Data tidak valid.'
    return render(request, 'portal/proof_upload.html', context)

@login_required
def proof_image(request, proof_id):
    proof = get_object_or_404(accessible_proofs(request.user), pk=proof_id)
    response = HttpResponse(bytes(proof.image), content_type='image/jpeg' if proof.image_type == 'jpeg' else 'image/png')
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'private, no-store'
    response['Content-Disposition'] = 'inline'
    return response

@login_required
@require_POST
def proof_verify(request, proof_id):
    with transaction.atomic():
        proof = get_object_or_404(TransferProof.objects.select_for_update().select_related('invoice__enrollment__student', 'invoice__enrollment__classroom__year'),pk=proof_id)
        invoice = Invoice.objects.select_for_update().get(pk=proof.invoice_id)
        student = proof.invoice.enrollment.student
        if not (request.user.is_active and request.user.is_superuser or Membership.objects.filter(user=request.user,school=student.school,role=Membership.Role.ADMIN,active=True).exists()) or proof.invoice.enrollment.classroom.year.school_id != student.school_id:
            raise Http404
        if proof.status != TransferProof.Status.PENDING or invoice.cancelled:
            return HttpResponseBadRequest('Bukti tidak dapat diverifikasi.')
        already_paid = invoice.payments.filter(verified=True).aggregate(total=Sum('amount'))['total'] or 0
        if proof.reported_amount > invoice.amount + invoice.fine - already_paid:
            return HttpResponseBadRequest('Nominal melebihi sisa tagihan.')
        Payment.objects.create(invoice=invoice,amount=proof.reported_amount,verified=True)
        proof.status = TransferProof.Status.VERIFIED
        proof.reviewed_by = request.user
        proof.reviewed_at = timezone.now()
        proof.save(update_fields=['status','reviewed_by','reviewed_at'])
    return redirect('proofs_list')

@login_required
def integration_settings(request):
    """Read-only configuration status; never return secret values."""
    import os
    if not request.user.is_active or not request.user.is_superuser:
        raise Http404
    groups = [
        ('Supabase PostgreSQL', ('POSTGRES_HOST', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD')),
        ('Gmail SMTP', ('SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD')),
        ('Midtrans', ('MIDTRANS_SERVER_KEY', 'MIDTRANS_CLIENT_KEY')),
    ]
    states = [{'name': name, 'configured': all(bool(os.environ.get(k)) for k in keys)} for name, keys in groups]
    return render(request, 'portal/integrations.html', {'states': states})

@login_required
def proof_edit(request, proof_id):
    proof = get_object_or_404(accessible_proofs(request.user).filter(guardian=request.user), pk=proof_id)
    if proof.status != TransferProof.Status.PENDING:
        raise Http404
    context = {'proof': proof}
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', ''))
            transfer_date = date.fromisoformat(request.POST.get('transfer_date', ''))
            if amount <= 0: raise ValueError('Nominal tidak valid.')
            data, kind = (proof.image, proof.image_type)
            if request.FILES.get('image'):
                data, kind = validate_image(request.FILES['image'])
            with transaction.atomic():
                locked = get_object_or_404(TransferProof.objects.select_for_update(),pk=proof_id,guardian=request.user)
                if locked.status != TransferProof.Status.PENDING: return HttpResponseBadRequest('Bukti tidak dapat diubah.')
                # Recheck active membership and guardian relationship after acquiring the lock.
                if not accessible_proofs(request.user).filter(pk=proof_id).exists(): raise Http404
                locked.reported_amount=amount; locked.transfer_date=transfer_date; locked.image=data; locked.image_type=kind
                locked.save(update_fields=['reported_amount','transfer_date','image','image_type'])
            return redirect('proofs_list')
        except (ValueError, OverflowError) as exc:
            context['error']=str(exc) or 'Data tidak valid.'
    return render(request, 'portal/proof_edit.html', context)

@login_required
@require_POST
def proof_withdraw(request, proof_id):
    with transaction.atomic():
        proof=get_object_or_404(TransferProof.objects.select_for_update(),pk=proof_id,guardian=request.user)
        if not accessible_proofs(request.user).filter(pk=proof_id).exists(): raise Http404
        if proof.status != TransferProof.Status.PENDING: return HttpResponseBadRequest('Bukti tidak dapat ditarik.')
        proof.status=TransferProof.Status.WITHDRAWN
        proof.save(update_fields=['status'])
    return redirect('proofs_list')
