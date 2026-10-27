"""Server-side read scopes for currently implemented dashboard queries.

These are not a substitute for database RLS and do not grant write access.
"""
from django.db.models import F, Q
from .models import Invoice, Membership

def scoped_invoices(user):
    if not user.is_authenticated:
        return Invoice.objects.none()
    scope = Q(pk__in=[])
    for m in Membership.objects.filter(user=user, active=True):
        school = Q(enrollment__student__school_id=m.school_id,
                   enrollment__classroom__year__school_id=m.school_id)
        if m.role == Membership.Role.ADMIN:
            scope |= school
        elif m.role == Membership.Role.GUARDIAN:
            scope |= school & Q(enrollment__student__guardians=user)
        elif m.role == Membership.Role.TEACHER:
            scope |= school & Q(enrollment__classroom__teachers=user)
    return Invoice.objects.filter(scope).distinct()

def aggregate_schools(user):
    if not user.is_authenticated:
        return []
    return list(Membership.objects.filter(user=user, active=True,
        role__in=[Membership.Role.PRINCIPAL, Membership.Role.FOUNDATION])
        .values_list('school_id', flat=True).distinct())

def aggregate_invoices(user):
    schools = aggregate_schools(user)
    return Invoice.objects.filter(enrollment__student__school_id__in=schools,
        enrollment__classroom__year__school_id=F('enrollment__student__school_id'),
        cancelled=False)
