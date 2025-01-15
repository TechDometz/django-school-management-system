from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.core import validators
import re
from datetime import date


def class_room_validator(value):
    """Ensure the classroom name is unique."""
    from .models import ClassRoom

    if ClassRoom.objects.filter(name=value).exists():
        raise ValidationError(_('"{}" already exists.'.format(value)))


def subject_validator(value):
    """Ensure the subject name is unique."""
    from .models import Subject

    if Subject.objects.filter(name=value).exists():
        raise ValidationError(_('"{}" subject already exists.'.format(value)))


def stream_validator(value):
    """Ensure the stream name is unique."""
    from .models import Stream

    if Stream.objects.filter(name=value).exists():
        raise ValidationError(_('"{}" stream already exists.'.format(value)))


def students_date_of_birth_validator(value):
    """
    Validate the student's date of birth to ensure the age is at least 13 years.
    """
    required_age = 13
    least_year_of_birth = date.today().year - required_age

    if value.year > least_year_of_birth:
        raise ValidationError(
            _(
                "Invalid date. The student must be at least {} years old.".format(
                    required_age
                )
            )
        )


@deconstructible
class ASCIIUsernameValidator(validators.RegexValidator):
    """
    Validator for ASCII-based usernames with a specific pattern.
    """

    regex = r"^[a-zA-Z]+\/[a-zA-Z0-9]{3}\/\d{4}$"
    message = _(
        "Enter a valid username. This value must follow the pattern: "
        "letters/three alphanumeric characters/four digits."
    )
    flags = re.ASCII
