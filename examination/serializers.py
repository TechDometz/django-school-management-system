from rest_framework import serializers

from .models import GradeScale, GradeScaleRule


class GradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScale
        fields = "__all__"


class GradeScaleRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScaleRule
        fields = "__all__"
