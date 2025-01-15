from rest_framework import serializers
from .models import (
    TeachersAttendance,
    AttendanceStatus,
    StudentAttendance,
    PeriodAttendance,
)


class AttendanceStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceStatus
        fields = "__all__"


class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher = (
        serializers.StringRelatedField()
    )  # Display teacher's name instead of the ID
    status = serializers.StringRelatedField()  # Display status name instead of ID
    date = serializers.DateField(format="%Y-%m-%d")  # Date format in response

    class Meta:
        model = TeachersAttendance
        fields = ["id", "teacher", "date", "time_in", "time_out", "status", "notes"]


class StudentAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()  # Display student name instead of ID
    status = serializers.StringRelatedField()  # Display status name instead of ID
    ClassRoom = serializers.StringRelatedField()  # Display classroom name instead of ID
    date = serializers.DateField(format="%Y-%m-%d")  # Date format in response

    class Meta:
        model = StudentAttendance
        fields = ["id", "student", "date", "ClassRoom", "status", "notes"]


class PeriodAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()  # Display student name instead of ID
    status = serializers.StringRelatedField()  # Display status name instead of ID
    date = serializers.DateField(format="%Y-%m-%d")  # Date format in response

    class Meta:
        model = PeriodAttendance
        fields = [
            "id",
            "student",
            "date",
            "period",
            "status",
            "reason_for_absence",
            "notes",
        ]
