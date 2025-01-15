from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404

from academic.models import Teacher
from .models import CustomUser as User, Accountant
from .serializers import (
    UserSerializer,
    UserSerializerWithToken,
    AccountantSerializer,
    TeacherSerializer,
)


# Custom Token View
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user_data = UserSerializerWithToken(self.user).data
        data.update(user_data)
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# User Views
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Accountant Views
class AccountantViewSet(viewsets.ModelViewSet):
    queryset = Accountant.objects.all()
    serializer_class = AccountantSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Override this method if you want to apply different permissions for different actions.
        """
        permissions = super().get_permissions()

        if self.action in ["update", "partial_update", "destroy"]:
            # Only admins can update or delete teachers
            permissions = [IsAdminUser()]
        return permissions

    def retrieve(self, request, pk=None):
        accountant = get_object_or_404(Accountant, pk=pk)
        serializer = self.get_serializer(accountant)
        return Response(serializer.data)

    def update(self, request, pk=None):
        accountant = get_object_or_404(Accountant, pk=pk)
        serializer = self.get_serializer(accountant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        accountant = get_object_or_404(Accountant, pk=pk)
        accountant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Teacher Views
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Override this method if you want to apply different permissions for different actions.
        """
        permissions = super().get_permissions()

        if self.action in ["update", "partial_update", "destroy"]:
            # Only admins can update or delete teachers
            permissions = [IsAdminUser()]
        return permissions

    def retrieve(self, request, pk=None):
        teacher = get_object_or_404(Teacher, pk=pk)
        serializer = self.get_serializer(teacher)
        return Response(serializer.data)

    def update(self, request, pk=None):
        teacher = get_object_or_404(Teacher, pk=pk)
        serializer = self.get_serializer(teacher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        teacher = get_object_or_404(Teacher, pk=pk)
        teacher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
