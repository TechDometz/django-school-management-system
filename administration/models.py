from django.db import models
from django.conf import settings
from datetime import date, datetime
from user_agents import parse

from .common_objs import *
from users.models import CustomUser


class Article(models.Model):
    title = models.CharField(max_length=150, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to="articles", blank=True, null=True)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CarouselImage(models.Model):
    title = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to="carousel")

    def __str__(self):
        return self.title


class AccessLog(models.Model):
    login = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL)
    ua = models.CharField(
        max_length=2000,
        help_text="User agent. We can use this to determine operating system and browser in use.",
    )
    date = models.DateTimeField(
        auto_now_add=True
    )  # Set this to add the timestamp on creation only
    ip = models.GenericIPAddressField()
    usage = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.login} - {self.usage} on {self.date}"

    def os(self):
        """
        Extract the operating system from the user agent string.
        Returns 'Unknown' if it cannot be detected.
        """
        try:
            user_agent = parse(self.ua)
            return user_agent.os.family
        except Exception as e:
            print(f"Error extracting OS from UA: {e}")
            return "Unknown"

    def browser(self):
        """
        Extract the browser from the user agent string.
        Returns 'Unknown' if it cannot be detected.
        """
        try:
            user_agent = parse(self.ua)
            return user_agent.browser.family
        except Exception as e:
            print(f"Error extracting Browser from UA: {e}")
            return "Unknown"

    class Meta:
        indexes = [
            models.Index(fields=["login"]),  # Add index for faster querying by login
            models.Index(fields=["date"]),  # Add index for faster querying by date
        ]


class School(models.Model):
    active = models.BooleanField(
        default=False,
        help_text="DANGER..!!!! If marked, this will be the default School Information System Wide...",
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    school_type = models.CharField(
        max_length=25, choices=SCHOOL_TYPE_CHOICE, blank=True, null=True
    )
    students_gender = models.CharField(
        max_length=25, choices=SCHOOL_STUDENTS_GENDER, blank=True, null=True
    )
    ownership = models.CharField(
        max_length=25, choices=SCHOOL_OWNERSHIP, blank=True, null=True
    )
    mission = models.TextField(blank=True, null=True)
    vision = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True)
    school_email = models.EmailField(blank=True, null=True)
    school_logo = models.ImageField(blank=True, null=True, upload_to="school_info")

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=["name"]),  # Index for quick searching by name
            models.Index(fields=["active"]),  # Index for filtering by active status
        ]
        ordering = ["name"]  # Default ordering by school name


class Day(models.Model):
    DAY_CHOICES = (
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    )
    day = models.IntegerField(choices=DAY_CHOICES, unique=True)

    def __str__(self):
        return (
            self.get_day_display()
        )  # Using get_day_display() to retrieve the display value for the day

    class Meta:
        ordering = ("day",)


class AcademicYear(models.Model):
    """
    A database table row that maps to every academic year.
    """

    name = models.CharField(max_length=255, unique=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    graduation_date = models.DateField(
        blank=True, null=True, help_text="The date when students graduate"
    )
    active_year = models.BooleanField(
        help_text="DANGER!! This is the current school year. "
        "There can only be one and setting this will remove it from other years. "
        "If you want to change the active year, click Admin, Change School Year."
    )

    class Meta:
        ordering = ("-start_date",)

    def __str__(self):
        return self.name

    @property
    def status(self):
        now_ = date.today()
        if self.active_year:
            return "active"
        elif self.start_date <= now_ <= self.end_date:
            return "pending"
        elif self.start_date > now_ > self.end_date:
            return "ended"
        return "unknown"  # Fallback in case status doesn't match any condition

    def save(self, *args, **kwargs):
        # Ensure only one active year at a time
        if self.active_year:
            AcademicYear.objects.exclude(pk=self.pk).update(active_year=False)
        super(AcademicYear, self).save(*args, **kwargs)

    def clean(self):
        """
        Add custom validation to ensure the end_date is after start_date if both are provided.
        """
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")


class Term(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Term 1", "Term 2"
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name="terms"
    )
    default_term_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=312500
    )
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"
