from rest_framework import serializers

from academic.models import (
    StudentsMedicalHistory,
    Student,
    Parent,
    ReasonLeft,
    ClassLevel,
    ClassYear,
)
from academic.serializers import ClassLevelSerializer, ClassYearSerializer


class ReasonLeftSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReasonLeft
        fields = "__all__"


class StudentHealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentsMedicalHistory
        fields = "__all__"


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    class_level = serializers.SerializerMethodField(read_only=True)
    class_of_year = serializers.SerializerMethodField(read_only=True)
    parent_guardian = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = "__all__"

    def get_class_level(self, obj):
        return obj.class_level.name if obj.class_level else None

    def get_class_of_year(self, obj):
        return obj.class_of_year.full_name if obj.class_of_year else None

    def get_parent_guardian(self, obj):
        return obj.parent_guardian.email if obj.parent_guardian else None

    def validate_and_create_student(self, data):
        """
        Reusable method to validate and create a student instance.
        """
        try:
            class_level = ClassLevel.objects.get(name__iexact=data.get("class_level"))
        except ClassLevel.DoesNotExist:
            raise serializers.ValidationError(
                f"Class level '{data['class_level']}' does not exist."
            )

        parent = None
        if "parent_contact" in data:
            parent, _ = Parent.objects.get_or_create(
                phone_number=data["parent_contact"],
                defaults={
                    "first_name": data.get("middle_name", "").title(),
                    "last_name": data.get("last_name", "").title(),
                    "email": f"parent_of_{data['first_name']}_{data['last_name']}@example.com",
                },
            )

        student = Student(
            first_name=data["first_name"].title(),
            middle_name=data.get("middle_name", "").title(),
            last_name=data["last_name"].title(),
            admission_number=data["admission_number"],
            parent_contact=data["parent_contact"],
            region=data["region"],
            city=data["city"],
            street=data.get("street", ""),
            class_level=class_level,
            gender=data["gender"],
            date_of_birth=data.get("date_of_birth", "2000-01-01"),
            std_vii_number=data.get("std_vii_number", ""),
            prems_number=data.get("prems_number", ""),
            parent_guardian=parent,
        )

        if "class_of_year" in data:
            try:
                class_year = ClassYear.objects.get(year=data["class_of_year"])
                student.class_of_year = class_year
            except ClassYear.DoesNotExist:
                raise serializers.ValidationError(
                    f"Class year '{data['class_of_year']}' does not exist."
                )

        student.save()
        return student

    def create(self, validated_data):
        """
        Single student creation using reusable method.
        """
        return self.validate_and_create_student(validated_data)

    def bulk_create(self, student_data_list):
        """
        Bulk creation of students.
        """
        created_students = []
        errors = []

        for data in student_data_list:
            try:
                student = self.validate_and_create_student(data)
                created_students.append(student)
            except serializers.ValidationError as e:
                data["error"] = str(e)
                errors.append(data)  # Collect data with errors for review

        return created_students, errors

