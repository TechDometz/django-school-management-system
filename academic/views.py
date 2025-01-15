from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.http import Http404

from .models import Teacher
from .serializers import TeacherSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing teacher instances.
    """

    queryset = Teacher.objects.all()  # Get all teacher objects
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get_permissions(self):
        """
        Override this method if you want to apply different permissions for different actions.
        """
        permissions = super().get_permissions()

        if self.action in ["update", "partial_update", "destroy"]:
            # Only admins can update or delete teachers
            permissions = [IsAdminUser()]
        return permissions

    def perform_create(self, serializer):
        """
        Override to handle any extra logic when creating a teacher, such as hashing passwords.
        """
        # Example: Hash password if 'password' field is included
        # if 'password' in serializer.validated_data:
        #     serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        serializer.save()

    def perform_update(self, serializer):
        """
        Override to handle any special logic when updating a teacher, such as password hashing.
        """
        # Example: Hash password if 'password' field is included
        # if 'password' in serializer.validated_data:
        #     serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        serializer.save()

    def perform_destroy(self, instance):
        """
        Override to handle any special logic before deleting a teacher.
        """
        # You can add any custom deletion logic here if needed
        instance.delete()
