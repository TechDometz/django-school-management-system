from rest_framework import serializers

from .models import (
    ClassYear,
    ClassRoom,
    GradeLevel,
    ClassLevel,
    Teacher,
    Subject,
    Department,
    Stream,
)


class ClassYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassYear
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = "__all__"


class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = "__all__"


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class GradeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeLevel
        fields = "__all__"


class ClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoom
        fields = "__all__"


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassYear
        fields = "__all__"
