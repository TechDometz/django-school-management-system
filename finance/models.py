from django.db import models

from academic.models import Student
from users.models import Accountant
from users.models import CustomUser as User


STATUS_CHOICES = [
    ("Pending", "Pending"),
    ("Completed", "Completed"),
    ("Cancelled", "Cancelled"),
]


class ReceiptAllocation(models.Model):
    name = models.CharField(max_length=255, null=True)
    abbr = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class PaymentAllocation(models.Model):
    name = models.CharField(max_length=255, null=True)
    abbr = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Receipt(models.Model):
    receipt_no = models.IntegerField(unique=True)
    date = models.DateField(auto_now_add=True)
    payer = models.CharField(max_length=255, null=True)
    paid_for = models.ForeignKey(
        ReceiptAllocation, on_delete=models.SET_NULL, null=True
    )
    student = models.ForeignKey(
        Student, on_delete=models.SET_NULL, blank=True, null=True
    )
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    received_by = models.ForeignKey(Accountant, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.date} - {self.paid_for} - {self.payer}"


class Payment(models.Model):
    payment_no = models.IntegerField(unique=True)
    date = models.DateField(auto_now_add=True)
    paid_to = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    paid_for = models.ForeignKey(
        PaymentAllocation, on_delete=models.SET_NULL, null=True
    )
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    paid_by = models.ForeignKey(Accountant, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.date} - {self.paid_for} - {self.paid_to}"
