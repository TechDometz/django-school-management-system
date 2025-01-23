from rest_framework import serializers

from academic.models import (
    StudentsMedicalHistory,
    Student,
    Parent,
    ReasonLeft,
    ClassLevel,
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
        class_level = obj.class_level
        serializer = ClassLevelSerializer(class_level, many=False)
        return serializer.data["name"]

    def get_class_of_year(self, obj):
        class_of_year = obj.class_of_year
        serializer = ClassYearSerializer(class_of_year, many=False)
        return serializer.data["full_name"]

    def get_parent_guardian(self, obj):
        parent_guardian = obj.parent_guardian
        serializer = ParentSerializer(parent_guardian, many=False)
        return serializer.data["email"]

    def create(self, validated_data):
        # Use validated_data instead of request.data for proper validation handling
        student = Student(
            first_name=validated_data["first_name"],
            middle_name=validated_data["middle_name"],
            last_name=validated_data["last_name"],
            admission_number=validated_data["addmission_number"],
            parent_contact=validated_data["parent_contact"],
            region=validated_data["region"],
            city=validated_data["city"],
            street=validated_data["street"],
            class_level=ClassLevel.objects.get(name=data["class_level"]),
            gender=validated_data["gender"],
            date_of_birth=validated_data["date_of_birth"],
        )

        # Optional: Handle 'class_of_year' if needed (assuming it's part of the request data)
        if "class_of_year" in validated_data:
            student.class_of_year = ClassYear.objects.get(
                year=validated_data["class_of_year"]
            )

        student.save()
        return student

    def bulk_create(self, student_data_list):
        # Assuming student_data_list is a list of dictionaries for bulk creation
        students = []
        for data in student_data_list:
            student = Student(
                first_name=data["first_name"].lower(),
                middle_name=data["middle_name"].lower(),
                last_name=data["last_name"].lower(),
                admission_number=data["addmission_number"],
                parent_contact=data["parent_contact"],
                region=data["region"],
                city=data["city"],
                class_level=ClassLevel.objects.get(name=data["class_level"]),
                gender=data["gender"],
                date_of_birth=data.get(
                    "date_of_birth", "2000-01-01"
                ),  # Default fallback
            )

            # Optional: Handle 'class_of_year' if needed
            if "class_of_year" in data:
                student.class_of_year = ClassYear.objects.get(
                    year=data["class_of_year"]
                )

            student.save()
            students.append(student)

        return students
