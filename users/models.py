from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import Group
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from administration.common_objs import *
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="first name"
    )
    middle_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="middle name"
    )
    last_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="last name"
    )
    email = models.EmailField(_("email address"), unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_accountant = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email


class Accountant(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="accountant",
        null=True,
        blank=True,
    )
    username = models.CharField(unique=True, max_length=250, blank=True)
    first_name = models.CharField(max_length=300, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=300, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICE, blank=True)
    email = models.EmailField(blank=True, null=True)
    empId = models.CharField(max_length=8, null=True, blank=True, unique=True)
    tin_number = models.CharField(max_length=9, null=True, blank=True)
    nssf_number = models.CharField(max_length=9, null=True, blank=True)
    salary = models.IntegerField(blank=True, null=True)
    unpaid_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    national_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=150, blank=True)
    alt_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Personal Email apart from the one given by the school",
    )
    date_of_birth = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to="Employee_images", blank=True, null=True)
    inactive = models.BooleanField(default=False)

    class Meta:
        ordering = ("first_name", "last_name")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def deleted(self):
        return self.inactive

    def save(self, *args, **kwargs):
        """
        When an accountant is created, generate a CustomUser instance for login.
        """
        # Generate unique username
        if not self.username:
            self.username = f"{self.first_name.lower()}{self.last_name.lower()}{get_random_string(4)}"

        if not self.user:
            # Create the user if it doesn't exist
            user = CustomUser.objects.create(
                first_name=self.first_name,
                last_name=self.last_name,
                email=self.email,
                is_accountant=True,
            )

            # Set a default password using empId (if available) or fallback
            default_password = f"Complex.{self.empId[-4:] if self.empId and len(self.empId) >= 4 else '0000'}"
            user.set_password(default_password)
            user.save()

            # Attach the created user to the accountant
            self.user = user

            # Add user to "accountant" group
            group, _ = Group.objects.get_or_create(name="accountant")
            user.groups.add(group)

        super().save(*args, **kwargs)

    def update_unpaid_salary(self):
        # Update unpaid salary at the start of each month
        current_month = timezone.now().month
        if self.unpaid_salary > 0:
            self.unpaid_salary += self.salary  # Add salary amount to unpaid salary
        else:
            self.unpaid_salary = (
                self.salary
            )  # If unpaid salary is 0, set the first month's salary
        self.save()
