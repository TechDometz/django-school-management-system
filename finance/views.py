from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404

from .models import Receipt, Payment
from .serializers import ReceiptSerializer, PaymentSerializer


# Receipts List & Create View using DRF's ListCreateAPIView
class ReceiptsListView(generics.ListCreateAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer

    def perform_create(self, serializer):
        # If you need custom logic, override the perform_create method
        serializer.save()


# Receipt Detail View (Retrieve, Update, Delete)
class ReceiptDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer


# Payment List & Create View using DRF's ListCreateAPIView
class PaymentListView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        # Custom logic can be added here before saving the object
        serializer.save()


# Payment Detail View (Retrieve, Update, Delete)
class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
