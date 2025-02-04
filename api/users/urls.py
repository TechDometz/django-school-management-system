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
    TeacherListView,
    TeacherDetailView,
    BulkUploadTeachersView,
)


urlpatterns = [
    # JWT Token endpoint
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/", UserListView.as_view(), name="users-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    # teacher URLs
    path("teachers/", TeacherListView.as_view(), name="teacher-list-create"),
    path("teachers/bulk-upload/", BulkUploadTeachersView.as_view(), name="teacher-bulk-upload"),
    path("teachers/<int:pk>/", TeacherDetailView.as_view(), name="accountant-detail"),
    # Accountant URLs
    path("accountants/", AccountantListView.as_view(), name="accountant-list-create"),
    path("accountants/<int:pk>/", AccountantDetailView.as_view(), name="accountant-detail"),
    # Parent URLs
    path("parents/", ParentListView.as_view(), name="parent-list-create"),
    path("parents/<int:pk>/", ParentDetailView.as_view(), name="parent-detail"),
  
]
