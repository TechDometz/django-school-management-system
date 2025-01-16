from rest_framework import serializers
from .models import AcademicYear, Term


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"


class TermSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)

    class Meta:
        model = Term
        fields = "__all__"
