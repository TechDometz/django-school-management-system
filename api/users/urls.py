from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import MyTokenObtainPairView, UserViewSet, AccountantViewSet

# Initialize the router
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"accountants", AccountantViewSet, basename="accountant")

urlpatterns = [
    # JWT Token endpoint
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Include ViewSet routes
    path("", include(router.urls)),
]
