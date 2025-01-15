from rest_framework import serializers


class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
