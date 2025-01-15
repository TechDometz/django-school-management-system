from django.urls import path
from attendance.views import (
    TeacherAttendanceListView,
    TeacherAttendanceDetailView,
    StudentAttendanceListView,
    StudentAttendanceDetailView,
    PeriodAttendanceListView,
    PeriodAttendanceDetailView,
)

urlpatterns = [
    path(
        "teacher-attendance/",
        TeacherAttendanceListView.as_view(),
        name="teacher-attendance-list",
    ),
    path(
        "teacher-attendance/<int:pk>/",
        TeacherAttendanceDetailView.as_view(),
        name="teacher-attendance-detail",
    ),
    path(
        "student-attendance/",
        StudentAttendanceListView.as_view(),
        name="student-attendance-list",
    ),
    path(
        "student-attendance/<int:pk>/",
        StudentAttendanceDetailView.as_view(),
        name="student-attendance-detail",
    ),
    path(
        "period-attendance/",
        PeriodAttendanceListView.as_view(),
        name="period-attendance-list",
    ),
    path(
        "period-attendance/<int:pk>/",
        PeriodAttendanceDetailView.as_view(),
        name="period-attendance-detail",
    ),
]
