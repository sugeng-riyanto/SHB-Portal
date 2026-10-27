from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from .access import aggregate_invoices, scoped_invoices
from .models import Membership

def home(request):
    return render(request, 'portal/home.html')

@login_required
def dashboard(request):
    memberships = Membership.objects.filter(user=request.user, active=True).select_related('school')
    invoices = scoped_invoices(request.user).select_related('enrollment__student','enrollment__classroom')[:100]
    summary = aggregate_invoices(request.user).aggregate(count=Count('id'), total=Sum('amount'))
    return render(request, 'portal/dashboard.html', {'memberships': memberships, 'invoices': invoices, 'summary': summary})

from django.http import HttpResponse, HttpResponseForbidden
from .imports import ImportErrorDetail, preview_xlsx, template_bytes, MAX_BYTES

def admin_only(user):
    return Membership.objects.filter(user=user, role=Membership.Role.ADMIN, active=True).exists()

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
