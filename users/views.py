from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404

from attendance.models import TeachersAttendance
from attendance.serializers import TeachersAttendanceSerializer

from .models import CustomUser as User, Accountant
from .serializers import UserSerializer, UserSerializerWithToken, AccountantSerializer


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
