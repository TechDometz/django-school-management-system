from django.urls import path, include
from sis.views import (
    # PhoneNumberViewSet, EmergencyContactViewSet, EmergencyContactNumberViewSet,
    # GradeLevelViewSet, ClassYearViewSet, StudentHealthRecordViewSet, GradeScaleViewSet,
    # GradeScaleRuleViewSet, SchoolYearViewSet, MessageToStudentViewSet,
    StudentListView,
    StudentDetailView,
    BulkUploadStudentsView,
)


urlpatterns = [
    path("students/", StudentListView.as_view(), name="students-list"),
    path("students/<int:pk>/", StudentDetailView.as_view(), name="student-detail"),
    path("upload/<filename>/", BulkUploadStudentsView.as_view()),
]
