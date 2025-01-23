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


class TeacherSerializer(serializers.ModelSerializer):
    # Accept a list of subject names for subject_specialization
    subject_specialization = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=True
    )
    subject_specialization_display = serializers.StringRelatedField(
        many=True, source="subject_specialization", read_only=True
    )

    class Meta:
        model = Teacher
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone_number",
            "empId",
            "short_name",
            "subject_specialization",
            "subject_specialization_display",
            "address",
            "gender",
            "date_of_birth",
            "salary",
        ]

    def validate_email(self, value):
        """
        Ensure the email is unique and valid.
        """
        if Teacher.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A teacher with this email already exists."
            )
        return value

    def validate_phone_number(self, value):
        """
        Ensure the phone number is unique.
        """
        if Teacher.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "A teacher with this phone number already exists."
            )
        return value

    def validate_subject_specialization(self, value):
        """
        Validate that the provided subject names exist in the database.
        """
        subjects = Subject.objects.filter(name__in=value).distinct()
        if len(subjects) != len(value):
            missing_subjects = set(value) - set(subjects.values_list("name", flat=True))
            raise serializers.ValidationError(
                f"The following subjects do not exist: {', '.join(missing_subjects)}"
            )
        return value

    def create(self, validated_data):
        """
        Handle the creation of a teacher instance with ManyToManyField.
        """
        subject_specialization_data = validated_data.pop("subject_specialization")
        teacher = Teacher.objects.create(**validated_data)
        subjects = Subject.objects.filter(name__in=subject_specialization_data)
        teacher.subject_specialization.set(subjects)
        return teacher
