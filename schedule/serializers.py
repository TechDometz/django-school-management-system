from rest_framework import serializers
from .models import Period
from academic.models import AllocatedSubject
from academic.serializers import (
    ClassRoomSerializer,
    SubjectSerializer,
)
from users.serializers import TeacherSerializer
from administration.serializers import TermSerializer


class PeriodSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)  # Include teacher details
    subject = SubjectSerializer(read_only=True)  # Include subject details
    classroom = ClassRoomSerializer(read_only=True)  # Include classroom details
    term = TermSerializer(read_only=True)  # Include term details

    class Meta:
        model = Period
        fields = [
            "id",
            "day_of_week",
            "start_time",
            "end_time",
            "teacher",
            "subject",
            "classroom",
            "term",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """
        Override create to handle dynamic assignment.
        """
        allocated_subject = validated_data.pop("allocated_subject", None)
        if not allocated_subject:
            raise serializers.ValidationError(
                {"error": "AllocatedSubject is required to create a period."}
            )

        teacher = allocated_subject.teacher
        subject = allocated_subject.subject
        classroom = allocated_subject.class_room
        term = allocated_subject.term

        return Period.objects.create(
            **validated_data,
            teacher=teacher,
            subject=subject,
            classroom=classroom,
            term=term,
        )
