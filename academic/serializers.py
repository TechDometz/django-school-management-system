from rest_framework import serializers


from .models import (
    ClassYear,
    ClassRoom,
    GradeLevel,
    ClassLevel,
    Subject,
    Department,
    Stream,
    ReasonLeft,
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


class StudentClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClass
        fields = "__all__"

    def validate(self, data):
        classroom = data.get("classroom")
        if classroom.occupied_sits >= classroom.capacity:
            raise serializers.ValidationError("This class is already full.")
        return data
