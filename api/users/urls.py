from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (
    MyTokenObtainPairView,
    UserViewSet,
    AccountantViewSet,
    TeacherViewSet,
    BulkUploadTeachersView,
)

# Initialize the router
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"accountants", AccountantViewSet, basename="accountant")
router.register(r"teachers", TeacherViewSet, basename="teacher")

urlpatterns = [
    # JWT Token endpoint
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("teachers/bulk-upload/", BulkUploadTeachersView.as_view()),
    # Include ViewSet routes
    path("", include(router.urls)),
]
