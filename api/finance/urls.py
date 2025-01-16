from django.urls import path
from finance.views import (
    ReceiptsListView,
    ReceiptDetailView,
    PaymentListView,
    PaymentDetailView,
    UpdateStudentDebtView,
)


urlpatterns = [
    path("receipts/", ReceiptsListView.as_view(), name="receipt-list"),
    path("receipts/<int:pk>/", ReceiptDetailView.as_view(), name="receipt-detail"),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path("payments/<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path(
        "update-student-debt/",
        UpdateStudentDebtView.as_view(),
        name="update-student-debt",
    ),
]
