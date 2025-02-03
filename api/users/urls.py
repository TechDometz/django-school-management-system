from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (
    MyTokenObtainPairView,
    UserListView,
    UserDetailView,
    ParentListView,
    ParentDetailView,
    AccountantListView,
    AccountantDetailView,
    TeacherViewSet,
    BulkUploadTeachersView,
)

# Initialize the router
router = DefaultRouter()
router.register(r"teachers", TeacherViewSet, basename="teacher")

urlpatterns = [
    # JWT Token endpoint
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/", UserListView.as_view(), name="users-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("teachers/bulk-upload/", BulkUploadTeachersView.as_view()),
    # Accountant URLs
    path("accountants/", AccountantListView.as_view(), name="accountant-list-create"),
    path("accountants/<int:pk>/", AccountantDetailView.as_view(), name="accountant-detail"),
    # Parent URLs
    path("parents/", ParentListView.as_view(), name="parent-list-create"),
    path("parents/<int:pk>/", ParentDetailView.as_view(), name="parent-detail"),
    # Include ViewSet routes
    path("", include(router.urls)),
]
