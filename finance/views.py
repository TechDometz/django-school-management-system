from django.http import Http404
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from academic.models import Student
from administration.models import Term
from django.utils.timezone import now
from .models import Receipt, Payment
from .serializers import ReceiptSerializer, PaymentSerializer


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# Receipts List & Create View using DRF's ListCreateAPIView
class ReceiptsListView(generics.ListCreateAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    pagination_class = CustomPagination
    filter_backends = [
        SearchFilter,
    ]
    filterset_fields = ["status", "date", "student"]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Override the create method to handle custom validation or processing.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the receipt and process student debt logic
        receipt = serializer.save()

        # Return response with detailed serialized data
        response_serializer = self.get_serializer(receipt)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# Receipt Detail View (Retrieve, Update, Delete)
class ReceiptDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Receipt not found.", code=404)


# Payment List & Create View using DRF's ListCreateAPIView
class PaymentListView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination
    filter_backends = [
        SearchFilter,
    ]
    filterset_fields = ["status", "date", "user"]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Example: Assign the logged-in user as the payer
        serializer.save(paid_by=self.request.user)


# Payment Detail View (Retrieve, Update, Delete)
class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Payment not found.", code=404)


class UpdateStudentDebtView(APIView):
    """
    API view to manually trigger student debt updates for the current term.
    """

    def post(self, request, *args, **kwargs):
        today = now().date()
        current_term = Term.objects.filter(
            start_date__lte=today, end_date__gte=today
        ).first()

        if not current_term:
            return Response(
                {"detail": "No active term found."}, status=status.HTTP_400_BAD_REQUEST
            )

        students = Student.objects.all()
        for student in students:
            student.update_debt_for_term(current_term)

        return Response(
            {"detail": "Student debts updated successfully."}, status=status.HTTP_200_OK
        )
