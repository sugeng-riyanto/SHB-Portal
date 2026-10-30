from django import template
from portal.models import Membership

register = template.Library()

@register.inclusion_tag('portal/sidebar.html', takes_context=True)
def portal_sidebar(context):
    request = context['request']
    user = request.user
    roles = set(Membership.objects.filter(user=user, active=True).values_list('role', flat=True)) if user.is_active else set()
    return {'request': request, 'is_super_admin': user.is_active and user.is_superuser,
            'is_admin': 'admin' in roles, 'is_principal': 'principal' in roles,
            'is_guardian': 'guardian' in roles}
