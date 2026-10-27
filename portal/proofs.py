"""Authorization and validation for transfer proofs."""
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from django.db.models import Q
from .models import Membership, TransferProof

MAX_IMAGE = 2 * 1024 * 1024
MAX_PIXELS = 16_000_000

def validate_image(upload):
    if upload.size > MAX_IMAGE:
        raise ValueError('Ukuran foto maksimal 2 MB.')
    data = upload.read(MAX_IMAGE + 1)
    if not data or len(data) > MAX_IMAGE:
        raise ValueError('Ukuran foto tidak valid.')
    try:
        with Image.open(BytesIO(data)) as image:
            if image.format not in ('JPEG', 'PNG') or image.width * image.height > MAX_PIXELS:
                raise ValueError('Gunakan JPG atau PNG maksimal 16 megapiksel.')
            image.verify()
            return data, image.format.lower()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValueError('Foto tidak valid.') from None

def accessible_proofs(user):
    if not user.is_authenticated:
        return TransferProof.objects.none()
    scope = Q(pk__in=[])
    for member in Membership.objects.filter(user=user, active=True):
        school = Q(invoice__enrollment__student__school_id=member.school_id,
                   invoice__enrollment__classroom__year__school_id=member.school_id)
        if member.role in (Membership.Role.ADMIN, Membership.Role.PRINCIPAL):
            scope |= school
        elif member.role == Membership.Role.TEACHER:
            scope |= school & Q(invoice__enrollment__classroom__teachers=user)
        elif member.role == Membership.Role.GUARDIAN:
            scope |= school & Q(guardian=user, invoice__enrollment__student__guardians=user)
    return TransferProof.objects.filter(scope).distinct()
