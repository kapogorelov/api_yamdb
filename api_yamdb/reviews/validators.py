from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Год выпуска не может быть больше текущего."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год выпуска ({value}) не может быть больше текущего '
            f'({current_year}).'
        )
    return value
