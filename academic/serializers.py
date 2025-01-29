from django.contrib.auth.models import Group
from rest_framework import serializers

from users.models import CustomUser

from .models import (
    ClassYear,
    ClassRoom,
    GradeLevel,
    ClassLevel,
    Teacher,
    Subject,
    Department,
    Stream,
    ReasonLeft,
    Parent,
    StudentClass,
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
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = Subject
        fields = "__all__"

    def validate_subject_code(self, value):
        # Add custom validation if needed (e.g., regex validation)
        if len(value) < 3:
            raise serializers.ValidationError(
                "Subject code must be at least 3 characters."
            )
        return value


class GradeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeLevel
        fields = "__all__"


class ClassRoomSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    stream = serializers.SerializerMethodField()
    class_teacher = serializers.SerializerMethodField()
    available_sits = serializers.ReadOnlyField()
    class_status = serializers.ReadOnlyField()

    class Meta:
        model = ClassRoom
        fields = "__all__"

    def get_name(self, obj):
        return obj.name.name  # Access the name field of the related ClassLevel object

    def get_stream(self, obj):
        return obj.stream.name  # Access the name field of the related Stream object

    def get_class_teacher(self, obj):
        return (
            f"{obj.class_teacher.first_name} {obj.class_teacher.last_name}"
            if obj.class_teacher
            else None
        )


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassYear
        fields = "__all__"


class ReasonLeftSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReasonLeft
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
            "id",
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


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = "__all__"

    def validate_email(self, value):
        if value and Parent.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A parent with this email already exists."
            )
        return value

    def validate_phone_number(self, value):
        if Parent.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "A parent with this phone number already exists."
            )
        return value

    def create(self, validated_data):
        email = validated_data.get("email", None)
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")

        # Create the parent object
        parent = super().create(validated_data)

        # Automatically create a user account for the parent
        if email:
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_parent": True,
                },
            )
            if created:
                # Set a default password
                default_password = f"{first_name.lower()}{last_name.lower()}123"
                user.set_password(default_password)
                user.save()

                # Assign to "parent" group
                group, _ = Group.objects.get_or_create(name="parent")
                user.groups.add(group)

        return parent

    def update(self, instance, validated_data):
        # Handle updating the associated CustomUser when parent data is updated
        email = validated_data.get("email", instance.email)
        first_name = validated_data.get("first_name", instance.first_name)
        last_name = validated_data.get("last_name", instance.last_name)

        if email:
            try:
                user = CustomUser.objects.get(email=instance.email)
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()
            except CustomUser.DoesNotExist:
                pass

        return super().update(instance, validated_data)


class StudentClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClass
        fields = "__all__"

    def validate(self, data):
        classroom = data.get("classroom")
        if classroom.occupied_sits >= classroom.capacity:
            raise serializers.ValidationError("This class is already full.")
        return data
