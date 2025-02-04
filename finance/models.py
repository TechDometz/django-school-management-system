from django.db import models
from academic.models import Student
from users.models import Accountant, CustomUser as User
from academic.models import Teacher


class PaymentStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    COMPLETED = "Completed", "Completed"
    CANCELLED = "Cancelled", "Cancelled"


class ReceiptAllocation(models.Model):
    name = models.CharField(max_length=255, null=True)
    abbr = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class PaymentAllocation(models.Model):
    name = models.CharField(max_length=255, null=True)
    abbr = models.CharField(max_length=50, blank=True, null=True)

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
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    received_by = models.ForeignKey(Accountant, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return (
            f"Receipt {self.receipt_no} | {self.date} | {self.paid_for} | {self.payer}"
        )

    def clean(self):
        if self.amount <= 0:
            raise ValueError("Amount must be a positive value.")

    def save(self, *args, **kwargs):
        """
        Custom save method to update the student's debt if the receipt is for 'School Fees'.
        """
        super().save(*args, **kwargs)  # Save the receipt first

        if (
            self.paid_for
            and self.paid_for.name.lower() == "school fees"
            and self.student
        ):
            # Reduce the student's debt by the amount paid
            self.student.clear_debt(self.amount)


class Payment(models.Model):
    payment_no = models.IntegerField(unique=True)
    date = models.DateField(auto_now_add=True)
    paid_to = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="payments")
    paid_for = models.ForeignKey(
        PaymentAllocation, on_delete=models.SET_NULL, null=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    paid_by = models.ForeignKey(Accountant, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Payment {self.payment_no} | {self.date} | {self.paid_for} | {self.paid_to}"

    def clean(self):
        if self.amount <= 0:
            raise ValueError("Amount must be a positive value.")

    def handle_salary_payment(self):
        # If paid_to is a teacher, reduce their unpaid salary
        if (
            self.paid_for.name.lower() == "salary"
        ):  # Assuming you track salary payment allocation
            if isinstance(self.paid_to, Teacher):
                self.paid_to.unpaid_salary -= self.amount
                self.paid_to.save()
            elif isinstance(self.paid_to, Accountant):
                self.paid_to.unpaid_salary -= self.amount
                self.paid_to.save()
        self.save()
