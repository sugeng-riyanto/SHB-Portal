from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from .access import scoped_invoices
from .students import safe_cell

@login_required
def invoice_export(request):
    # Use the same enforced scope as the dashboard; never accept user-supplied school IDs.
    records=scoped_invoices(request.user).select_related('enrollment__student','enrollment__classroom').order_by('due_date','id')
    book=Workbook();sheet=book.active;sheet.title='Bills'
    sheet.append(['SHB Portal export (not a payment receipt)'])
    sheet.append(['Generated (UTC)',timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')])
    sheet.append(['Student','Class','Bill','Amount IDR','Fine IDR','Due date','Status'])
    for invoice in records.iterator():
        sheet.append([safe_cell(invoice.enrollment.student.name),safe_cell(invoice.enrollment.classroom.name),safe_cell(invoice.description),invoice.amount,invoice.fine,invoice.due_date.isoformat(),'Cancelled' if invoice.cancelled else 'Active'])
    stream=BytesIO();book.save(stream)
    response=HttpResponse(stream.getvalue(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition']='attachment; filename="shb-bills.xlsx"';response['Cache-Control']='private, no-store'
    return response
