from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
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

def dashboard_greeting(now=None):
    from zoneinfo import ZoneInfo
    from django.utils import timezone
    now = now or timezone.now()
    hour = now.astimezone(ZoneInfo('Asia/Jakarta')).hour
    if 5 <= hour < 11: return 'Selamat pagi'
    if 11 <= hour < 15: return 'Selamat siang'
    if 15 <= hour < 18: return 'Selamat sore'
    return 'Selamat malam'

@login_required
def dashboard(request):
    memberships = list(Membership.objects.filter(user=request.user, active=True).select_related('school'))
    is_super_admin = bool(request.user.is_active and request.user.is_superuser)
    is_school_admin = any(m.role == Membership.Role.ADMIN for m in memberships) and not is_super_admin
    invoices = list(scoped_invoices(request.user).select_related('enrollment__student','enrollment__classroom','receipt')[:100])
    guardian_schools = set(Membership.objects.filter(user=request.user, role=Membership.Role.GUARDIAN, active=True).values_list('school_id', flat=True))
    linked_students = set(request.user.linked_students.values_list('id', flat=True))
    for invoice in invoices:
        invoice.may_upload_proof = invoice.enrollment.student.school_id in guardian_schools and invoice.enrollment.student_id in linked_students and not invoice.cancelled
    aggregate_query = aggregate_invoices(request.user)
    if is_school_admin:
        aggregate_query = scoped_invoices(request.user).filter(cancelled=False)
    summary = aggregate_query.aggregate(count=Count('id'), total=Sum('amount'))
    # Leadership aggregate and individual scopes remain separate; no student names in chart.
    chart_query = aggregate_query if aggregate_query.exists() else scoped_invoices(request.user).filter(cancelled=False)
    months = list(chart_query.annotate(month=TruncMonth('due_date')).values('month').annotate(count=Count('id')).order_by('month')[:24])
    maximum = max((m['count'] for m in months), default=1)
    for month in months: month['width'] = round(100 * month['count'] / maximum)
    return render(request, 'portal/dashboard.html', {'memberships': memberships, 'invoices': invoices, 'summary': summary, 'months': months, 'is_super_admin': is_super_admin, 'is_school_admin': is_school_admin, 'greeting': dashboard_greeting(), 'display_name': request.user.get_full_name().strip() or request.user.get_username()})

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
    from .students import admin_school_ids
    from .models import School
    from .imports import match_rows
    schools = School.objects.filter(pk__in=admin_school_ids(request.user))
    context = {'schools': schools}
    if request.method == 'POST':
        request.session.pop('invoice_import_preview', None)
        uploaded = request.FILES.get('file')
        school = schools.filter(pk=request.POST.get('school') if request.POST.get('school', '').isdigit() else None).first()
        if not school:
            context['error'] = 'Pilih sekolah yang menjadi lingkup akses Anda.'
        elif not uploaded or uploaded.size > MAX_BYTES or not uploaded.name.lower().endswith('.xlsx'):
            context['error'] = 'Pilih file XLSX maksimal 2 MB.'
        else:
            try:
                import secrets
                from django.utils import timezone
                rows = match_rows(preview_xlsx(uploaded.read(MAX_BYTES + 1)), school)
                context['rows'] = rows
                context['school_selected'] = school
                if rows:
                    token = secrets.token_urlsafe(24)
                    request.session['invoice_import_preview'] = {'school':school.pk,'rows':rows,'token':token,'created':timezone.now().isoformat()}
                    context['commit_token'] = token
                context['previewed'] = True
            except ImportErrorDetail as exc:
                context['error'] = str(exc)
    return render(request, 'portal/import_preview.html', context)

@login_required
def invoice_import_commit(request):
    import secrets
    from datetime import datetime, timedelta
    from django.db import IntegrityError, transaction
    from django.http import HttpResponseBadRequest
    from django.shortcuts import get_object_or_404, redirect
    from django.utils import timezone
    from .students import admin_school_ids
    from .imports import match_rows
    from .models import School, Invoice, ActivityEvent
    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])
    batch=request.session.get('invoice_import_preview')
    if not batch or not secrets.compare_digest(str(request.POST.get('token','')),batch['token']):
        return HttpResponseBadRequest('Preview tidak tersedia atau sudah digunakan.')
    try:
        if timezone.now() - datetime.fromisoformat(batch['created']) > timedelta(minutes=20):
            request.session.pop('invoice_import_preview',None)
            return HttpResponseBadRequest('Preview kedaluwarsa; unggah ulang.')
    except (ValueError,TypeError):
        return HttpResponseBadRequest('Preview tidak valid.')
    school=get_object_or_404(School,pk=batch['school'],pk__in=admin_school_ids(request.user))
    selected=request.POST.getlist('rows')
    if not selected or len(selected)!=len(set(selected)) or any(not x.isdigit() for x in selected):
        return HttpResponseBadRequest('Pilih baris yang valid.')
    selected_ids={int(x) for x in selected}
    rows=[row for row in batch['rows'] if row['row'] in selected_ids]
    if len(rows)!=len(selected_ids) or any(row['errors'] for row in rows):
        return HttpResponseBadRequest('Baris tidak valid; unggah ulang.')
    try:
        with transaction.atomic():
            School.objects.select_for_update().get(pk=school.pk)
            match_rows(rows,school,lock_banks=True)
            if any(row['errors'] for row in rows):
                return HttpResponseBadRequest('Data berubah; unggah ulang dan periksa kembali.')
            for row in rows:
                bank = row.get('bank_snapshot') or {}
                Invoice.objects.create(enrollment_id=row['enrollment_id'],reference=row['reference'],
                    description=row['description'] or row['bill_type'],amount=row['amount'],fine=row['fine'],
                    due_date=row['due_date'],virtual_account=row['va'],imported_type=row['bill_type'],imported_period=row['period'],
                    payment_account_id=bank.get('id'), payment_bank_name=bank.get('bank',''),
                    payment_account_name=bank.get('name',''), payment_account_number=bank.get('number',''))
            ActivityEvent.objects.create(school=school,actor=request.user,action='invoice_import')
    except IntegrityError:
        return HttpResponseBadRequest('Konflik data; tidak ada tagihan disimpan. Unggah ulang.')
    request.session.pop('invoice_import_preview',None)
    return redirect('dashboard')

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
    proofs_query = accessible_proofs(request.user).select_related('invoice__enrollment__student', 'invoice__enrollment__classroom')
    class_filter = request.GET.get('class', '').strip()[:20]
    if class_filter:
        proofs_query = proofs_query.filter(invoice__enrollment__classroom__name=class_filter)
    proofs = list(proofs_query[:100])
    admin_schools = set(Membership.objects.filter(user=request.user, active=True, role=Membership.Role.ADMIN).values_list('school_id', flat=True))
    if request.user.is_active and request.user.is_superuser:
        from .models import School
        admin_schools.update(School.objects.values_list('id', flat=True))
    for proof in proofs:
        proof.may_verify = proof.invoice.enrollment.student.school_id in admin_schools
        proof.may_edit = proof.guardian_id == request.user.id and proof.status == TransferProof.Status.PENDING
        proof.may_comment = proof.guardian_id == request.user.id or proof.may_verify
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
        from .receipts import issue_if_paid
        issue_if_paid(invoice)
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

@login_required
@require_POST
def proof_bulk_verify(request):
    raw = request.POST.getlist('proof_ids')
    if not raw or len(raw) > 100 or any(not value.isdigit() for value in raw):
        return HttpResponseBadRequest('Pilih 1–100 bukti yang valid.')
    ids = sorted(set(int(value) for value in raw))
    if len(ids) != len(raw):
        return HttpResponseBadRequest('Pilihan bukti duplikat.')
    try:
        with transaction.atomic():
            proofs = list(TransferProof.objects.select_for_update().filter(pk__in=ids).select_related('invoice__enrollment__student', 'invoice__enrollment__classroom__year').order_by('pk'))
            if len(proofs) != len(ids): raise ValueError('Bukti tidak tersedia.')
            for proof in proofs:
                student = proof.invoice.enrollment.student
                if not (request.user.is_active and request.user.is_superuser or Membership.objects.filter(user=request.user,school=student.school,role=Membership.Role.ADMIN,active=True).exists()): raise ValueError('Bukti di luar hak akses.')
                if proof.invoice.enrollment.classroom.year.school_id != student.school_id: raise ValueError('Sekolah tidak sesuai.')
                invoice = Invoice.objects.select_for_update().get(pk=proof.invoice_id)
                if proof.status != TransferProof.Status.PENDING or invoice.cancelled: raise ValueError('Bukti sudah diproses atau tagihan dibatalkan.')
                paid = invoice.payments.filter(verified=True).aggregate(total=Sum('amount'))['total'] or 0
                if proof.reported_amount > invoice.amount + invoice.fine - paid: raise ValueError('Nominal melebihi sisa tagihan.')
                Payment.objects.create(invoice=invoice,amount=proof.reported_amount,verified=True)
                from .receipts import issue_if_paid
                issue_if_paid(invoice)
                proof.status=TransferProof.Status.VERIFIED;proof.reviewed_by=request.user;proof.reviewed_at=timezone.now()
                proof.save(update_fields=['status','reviewed_by','reviewed_at'])
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))
    return redirect('proofs_list')

@login_required
def proof_comments(request, proof_id):
    from .models import ProofComment
    proof=get_object_or_404(accessible_proofs(request.user).select_related('invoice__enrollment__student'),pk=proof_id)
    school_id=proof.invoice.enrollment.student.school_id
    is_admin=request.user.is_active and (request.user.is_superuser or Membership.objects.filter(user=request.user,school_id=school_id,role=Membership.Role.ADMIN,active=True).exists())
    if proof.guardian_id != request.user.id and not is_admin: raise Http404
    error=None
    if request.method=='POST':
        body=request.POST.get('body','').strip()
        if not body or len(body)>1000: error='Komentar wajib diisi, maksimal 1.000 karakter.'
        else:
            ProofComment.objects.create(proof=proof,sender=request.user,body=body)
            return redirect('proof_comments',proof_id=proof.pk)
    return render(request,'portal/proof_comments.html',{'proof':proof,'comments':proof.comments.select_related('sender').order_by('created_at'),'error':error})
