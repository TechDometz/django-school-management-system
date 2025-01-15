from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import Group
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

    def __str__(self):
        return self.email


class Accountant(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="accountant_profile"
    )
    empId = models.CharField(max_length=8, null=True, blank=True, unique=True)
    tin_number = models.CharField(max_length=9, null=True, blank=True)
    nssf_number = models.CharField(max_length=9, null=True, blank=True)
    salary = models.IntegerField(blank=True, null=True)
    national_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=150, blank=True)
    alt_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Personal Email apart from the one given by the school",
    )
    date_of_birth = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to="employee_images", blank=True, null=True)
    inactive = models.BooleanField(default=False)

    class Meta:
        ordering = ("user__first_name", "user__last_name")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


@receiver(post_save, sender=Accountant)
def create_accountant_user(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user.is_accountant = True
        user.set_password(CustomUser.objects.make_random_password())
        user.save()

        group, _ = Group.objects.get_or_create(name="accountant")
        user.groups.add(group)

        # Send an email with credentials or a password reset link
        # mail_agent(user.alt_email, "Welcome", "Your credentials...")
