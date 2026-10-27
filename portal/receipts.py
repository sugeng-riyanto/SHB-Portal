"""Payment receipt issuance and restricted verification.

Identifiers are not authentication. All views check the signed-in user's scope.
"""
import secrets
import string
import uuid
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import qrcode
from .access import scoped_invoices
from .models import Membership, PaymentReceipt


def issue_if_paid(invoice):
    # Caller must hold the invoice row lock and be inside a DB transaction.
    if invoice.cancelled:
        return None
    total=invoice.payments.filter(verified=True).aggregate(total=Sum('amount'))['total'] or 0
    due=invoice.amount+invoice.fine
    if total < due:
        return None
    code=''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(6))
    receipt,_=PaymentReceipt.objects.get_or_create(invoice=invoice,defaults={'number':'SHB-'+uuid.uuid4().hex.upper(),'verification_code':code,'amount':total})
    return receipt

def receipt_is_current(receipt):
    paid=receipt.invoice.payments.filter(verified=True).aggregate(total=Sum('amount'))['total'] or 0
    return not receipt.invoice.cancelled and paid == receipt.amount and paid == receipt.invoice.amount + receipt.invoice.fine

def receipt_for_user(user,receipt_id):
    invoice_ids=scoped_invoices(user).values('pk')
    receipt=get_object_or_404(PaymentReceipt.objects.select_related('invoice__enrollment__student','invoice__enrollment__classroom'),pk=receipt_id,invoice_id__in=invoice_ids,invoice__cancelled=False)
    if not receipt_is_current(receipt): raise Http404
    return receipt

@login_required
def download_pdf(request,receipt_id):
    receipt=receipt_for_user(request.user,receipt_id)
    verify_url=request.build_absolute_uri(reverse('receipt_verify'))+'?number='+receipt.number+'&code='+receipt.verification_code
    qr=qrcode.make(verify_url); qr_data=BytesIO();qr.save(qr_data,format='PNG');qr_data.seek(0)
    output=BytesIO();pdf=canvas.Canvas(output,pagesize=A4)
    pdf.setTitle('SHB Portal Payment Receipt')
    pdf.setFont('Helvetica-Bold',18);pdf.drawString(48,790,'SHB Portal - Payment Receipt')
    pdf.setFont('Helvetica',11)
    lines=[f'Receipt: {receipt.number}',f'Verification code: {receipt.verification_code}',f'Student: {receipt.invoice.enrollment.student.name}',f'Class: {receipt.invoice.enrollment.classroom.name}',f'Bill: {receipt.invoice.description}',f'Amount verified: IDR {receipt.amount:,}',f'Issued: {receipt.issued_at:%Y-%m-%d %H:%M UTC}', 'Verification requires an authorized school administrator login.']
    for i,line in enumerate(lines): pdf.drawString(48,750-i*25,line[:100])
    pdf.drawImage(ImageReader(qr_data),48,430,width=120,height=120)
    pdf.showPage();pdf.save()
    response=HttpResponse(output.getvalue(),content_type='application/pdf')
    response['Content-Disposition']=f'attachment; filename="{receipt.number}.pdf"'
    response['Cache-Control']='private, no-store';response['X-Content-Type-Options']='nosniff'
    return response

@login_required
def verify(request):
    from .students import admin_school_ids
    school_ids=admin_school_ids(request.user)
    if not school_ids.exists(): raise Http404
    number=request.GET.get('number','').strip().upper()[:40]
    code=request.GET.get('code','').strip().upper()[:6]
    receipt=None
    if number and code:
        receipt=PaymentReceipt.objects.filter(number=number,verification_code=code,invoice__enrollment__student__school_id__in=school_ids,invoice__enrollment__classroom__year__school_id=F('invoice__enrollment__student__school_id'),invoice__cancelled=False).select_related('invoice__enrollment__student').first()
    if receipt and not receipt_is_current(receipt): receipt=None
    response=render(request,'portal/receipt_verify.html',{'receipt':receipt,'searched':bool(number and code),'number':number,'code':code})
    response['Cache-Control']='private, no-store'
    return response
