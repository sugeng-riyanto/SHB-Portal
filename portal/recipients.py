"""Build a scoped recipient list; no network delivery in this module."""
from django.contrib.auth import get_user_model
from .models import Classroom, Membership
from .students import admin_school_ids


def class_recipients(user, classroom_id):
    """Return active guardians of pupils enrolled in a class the admin controls."""
    classroom = Classroom.objects.filter(pk=classroom_id, year__school_id__in=admin_school_ids(user)).first()
    if classroom is None:
        return get_user_model().objects.none()
    return get_user_model().objects.filter(
        is_active=True,
        membership__school_id=classroom.year.school_id,
        membership__role=Membership.Role.GUARDIAN,
        membership__active=True,
        linked_students__school_id=classroom.year.school_id,
        linked_students__enrollment__classroom=classroom,
    ).exclude(email='').distinct().order_by('email','pk')
