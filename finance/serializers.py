from rest_framework import serializers
from .models import Receipt, Payment, ReceiptAllocation, PaymentAllocation
from academic.models import Student
from users.models import CustomUser, Accountant
from sis.serializers import StudentSerializer
from users.serializers import AccountantSerializer, UserSerializer


class ReceiptAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptAllocation
        fields = ["id", "name", "abbr"]


class PaymentAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAllocation
        fields = ["id", "name", "abbr"]


class ReceiptSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all()
    )  # Allow passing student ID for creation
    paid_for = serializers.PrimaryKeyRelatedField(
        queryset=ReceiptAllocation.objects.all()
    )  # Allow passing ReceiptAllocation ID for creation
    received_by = serializers.PrimaryKeyRelatedField(
        queryset=Accountant.objects.all()
    )  # Allow passing Accountant ID for creation

    student_details = StudentSerializer(read_only=True, source="student")
    paid_for_details = ReceiptAllocationSerializer(read_only=True, source="paid_for")
    received_by_details = AccountantSerializer(read_only=True, source="received_by")

    class Meta:
        model = Receipt
        fields = (
            "id",
            "receipt_no",
            "date",
            "payer",
            "paid_for",
            "paid_for_details",  # Embedded ReceiptAllocation details
            "student",
            "student_details",  # Embedded Student details
            "amount",
            "status",
            "received_by",
            "received_by_details",  # Embedded Accountant details
        )

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive value.")
        return value

    def create(self, validated_data):
        """
        Override create to handle debt reduction when a receipt is created.
        """
        receipt = Receipt.objects.create(**validated_data)

        # Handle student debt reduction if paid_for is "School Fees"
        if (
            receipt.paid_for
            and receipt.paid_for.name.lower() == "school fees"
            and receipt.student
        ):
            receipt.student.clear_debt(receipt.amount)

        return receipt


class PaymentSerializer(serializers.ModelSerializer):
    paid_for = PaymentAllocationSerializer(read_only=True)
    paid_by = AccountantSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    paid_for_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentAllocation.objects.all(), source="paid_for", write_only=True
    )
    paid_by_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="paid_by", write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_no",
            "date",
            "paid_to",
            "amount",
            "status",
            "paid_for",
            "paid_by",
            "user",
            "paid_for_id",
            "paid_by_id",
            "user_id",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive value.")
        return value
