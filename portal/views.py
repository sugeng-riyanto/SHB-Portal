from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from .models import Invoice, Membership

def home(request):
    return render(request, 'portal/home.html')

@login_required
def dashboard(request):
    memberships = Membership.objects.filter(user=request.user, active=True).select_related('school')
    scope = Q(pk__in=[])
    for m in memberships:
        school = Q(enrollment__student__school_id=m.school_id)
        if m.role == Membership.Role.ADMIN:
            scope |= school
        elif m.role == Membership.Role.GUARDIAN:
            scope |= school & Q(enrollment__student__guardians=request.user)
        elif m.role == Membership.Role.TEACHER:
            scope |= school & Q(enrollment__classroom__teachers=request.user)
    invoices = Invoice.objects.filter(scope).select_related('enrollment__student','enrollment__classroom').distinct()[:100]
    return render(request, 'portal/dashboard.html', {'memberships': memberships, 'invoices': invoices})
