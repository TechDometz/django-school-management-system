from rest_framework import serializers
from .models import *
from academic.models import Student
from users.models import CustomUser
from academic.serializers import StudentSerializer
from users.serializers import AccountantSerializer, UserSerializer


class ReceiptAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptAllocation
        fields = "__all__"


class PaymentAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAllocation
        fields = "__all__"


class ReceiptSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)  # Embed StudentSerializer directly
    paid_for = ReceiptAllocationSerializer(
        read_only=True
    )  # Embed ReceiptAllocationSerializer
    received_by = AccountantSerializer(read_only=True)  # Embed AccountantSerializer

    class Meta:
        model = Receipt
        fields = (
            "id",
            "receipt_no",
            "date",
            "student",
            "paid_for",
            "payer",
            "amount",
            "received_by",
        )

    def create(self, validated_data):
        # Assuming all necessary fields are validated correctly before this
        student = validated_data["student"]
        paid_for = validated_data["paid_for"]
        received_by = validated_data["received_by"]

        receipt = Receipt.objects.create(
            receipt_no=validated_data["receipt_no"],
            payer=validated_data["payer"],
            amount=validated_data["amount"],
            student=student,
            paid_for=paid_for,
            received_by=received_by,
        )
        return receipt


class PaymentSerializer(serializers.ModelSerializer):
    paid_for = PaymentAllocationSerializer(read_only=True)
    paid_by = AccountantSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"

    def create(self, validated_data):
        # Assuming all necessary fields are validated correctly before this
        paid_for = validated_data["paid_for"]
        paid_by = validated_data["paid_by"]

        payment = Payment.objects.create(
            payment_no=validated_data["payment_no"],
            paid_to=validated_data["paid_to"],
            amount=validated_data["amount"],
            paid_for=paid_for,
            paid_by=paid_by,
        )
        return payment
