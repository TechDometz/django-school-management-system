import openpyxl
from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404

from academic.models import Teacher, Subject
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


class BulkUploadTeachersView(APIView):
    """
    API View to handle bulk uploading of teachers from an Excel file.
    """

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Load the Excel file
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active  # Assuming data is in the first sheet

            # Expected columns in the Excel file
            columns = [
                "first_name",
                "middle_name",
                "last_name",
                "phone_number",
                "employment_id",
                "subject_specialization",  # Should match subject names as a comma-separated string
                "address",
                "gender",
                "date_of_birth",
                "salary",
            ]

            teachers_to_create = []
            for i, row in enumerate(
                sheet.iter_rows(min_row=2, values_only=True), start=2
            ):
                # Map row data to the expected columns
                teacher_data = dict(zip(columns, row))

                try:
                    # Generate email based on first_name and last_name
                    generated_email = (
                        f"{teacher_data['first_name'].lower()}."
                        f"{teacher_data['last_name'].lower()}@hayatul.com"
                    )
                    teacher_data["email"] = generated_email

                    # Check for duplicate email
                    if Teacher.objects.filter(email=generated_email).exists():
                        return Response(
                            {
                                "error": f"Row {i}: Email '{generated_email}' already exists."
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Check for duplicate phone number
                    if Teacher.objects.filter(
                        phone_number=teacher_data["phone_number"]
                    ).exists():
                        return Response(
                            {"error": f"Row {i}: Phone number already exists."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Validate subject specialization
                    subjects = []
                    subject_names = (
                        teacher_data["subject_specialization"].lower().split(",")
                        if teacher_data["subject_specialization"].lower()
                        else []
                    )
                    for subject_name in subject_names:
                        try:
                            subject = Subject.objects.get(name=subject_name.strip())
                            subjects.append(subject)
                        except Subject.DoesNotExist:
                            return Response(
                                {
                                    "error": f"Row {i}: Subject '{subject_name.strip()}' does not exist."
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                    # Create Teacher object
                    teacher = Teacher(
                        first_name=teacher_data["first_name"].lower(),
                        middle_name=teacher_data["middle_name"].lower(),
                        last_name=teacher_data["last_name"].lower(),
                        email=generated_email,
                        phone_number=teacher_data["phone_number"],
                        empId=teacher_data["employment_id"],
                        address=teacher_data["address"],
                        gender=teacher_data["gender"],
                        date_of_birth=teacher_data["date_of_birth"],
                        salary=teacher_data["salary"],
                    )
                    teacher.save()

                    # Assign subjects
                    if subjects:
                        teacher.subject_specialization.set(subjects)

                    # Create corresponding user
                    if not teacher.username:
                        teacher.username = f"{teacher.first_name.lower()}{teacher.last_name.lower()}{get_random_string(4)}"
                    teacher.save()

                    user, created = User.objects.get_or_create(
                        email=teacher.email,
                        defaults={
                            "first_name": teacher.first_name,
                            "last_name": teacher.last_name,
                            "is_teacher": True,
                        },
                    )
                    if created:
                        default_password = f"Complex.{teacher.empId[-4:] if teacher.empId and len(teacher.empId) >= 4 else '0000'}"
                        user.set_password(default_password)
                        user.save()

                        # Add to "teacher" group
                        group, _ = Group.objects.get_or_create(name="teacher")
                        user.groups.add(group)

                    teachers_to_create.append(teacher)

                except Exception as e:
                    return Response(
                        {"error": f"Row {i}: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                {
                    "message": f"{len(teachers_to_create)} teachers successfully uploaded."
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
