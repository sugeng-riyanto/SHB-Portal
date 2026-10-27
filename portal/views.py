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
