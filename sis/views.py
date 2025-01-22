import openpyxl
from rest_framework import views
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

from academic.models import Student, GradeLevel, Parent
from .serializers import StudentSerializer


class StudentListView(views.APIView):
    """
    List all students, or create a new student.
    """

    # permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = StudentSerializer(data=request.data)

        print(serializer.is_valid())
        print(request.data)
        if serializer.is_valid():
            student = serializer.create(request)
            if student:
                # serializer.save()
                return Response(data=student, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        student = self.get_object(pk)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        student = self.get_object(pk)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        student = self.get_object(pk)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BulkUploadStudentsView(APIView):
    """
    API View to handle bulk uploading of students from an Excel file.
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
                "admission_number",
                "parent_contact",
                "region",
                "city",
                "grade_level",
                "gender",
                "date_of_birth",
            ]

            students_to_create = []
            sibling_relationships = []  # To store sibling pairs for linking

            for i, row in enumerate(
                sheet.iter_rows(min_row=2, values_only=True), start=2
            ):
                # Map row data to the expected columns
                student_data = dict(zip(columns, row))

                # Validate and prepare the data
                try:
                    grade_level = GradeLevel.objects.get(
                        name=student_data["grade_level"]
                    )
                except GradeLevel.DoesNotExist as e:
                    return Response(
                        {"error": f"Row {i}: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Handle parent relationship
                parent_contact = student_data["parent_contact"]
                parent = None
                if parent_contact:
                    parent, _ = Parent.objects.get_or_create(
                        phone_number=parent_contact,
                        defaults={
                            "first_name": student_data["middle_name"],
                            "last_name": student_data["last_name"],
                            "email": f"parent_{student_data['first_name']}_{student_data['last_name']}@hayatul.com",
                        },
                    )

                # Check for existing siblings
                existing_sibling = Student.objects.filter(
                    parent_contact=parent_contact
                ).first()

                # Prepare the student instance
                student = Student(
                    first_name=student_data["first_name"],
                    middle_name=student_data["middle_name"],
                    last_name=student_data["last_name"],
                    admission_number=student_data["admission_number"],
                    parent_contact=parent_contact,
                    region=student_data["region"],
                    city=student_data["city"],
                    grade_level=grade_level,
                    gender=student_data["gender"],
                    date_of_birth=student_data["date_of_birth"],
                    parent_guardian=parent,  # Assign the parent to the student
                )
                students_to_create.append(student)

                # Store sibling relationships for later processing
                if existing_sibling:
                    sibling_relationships.append((student, existing_sibling))

            # Bulk create students
            Student.objects.bulk_create(students_to_create)

            # Link sibling relationships
            for new_student, sibling in sibling_relationships:
                new_student.siblings.add(sibling)
                sibling.siblings.add(new_student)

            return Response(
                {
                    "message": f"{len(students_to_create)} students successfully uploaded."
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


"""
class StudentHealthRecordViewSet(viewsets.ModelViewSet):
	queryset = StudentHealthRecord.objects.all()
	serializer_class = StudentHealthRecordSerializer

class GradeScaleViewSet(viewsets.ModelViewSet):
	queryset = GradeScale.objects.all()
	serializer_class = GradeScaleSerializer

class GradeScaleRuleViewSet(viewsets.ModelViewSet):
	queryset = GradeScaleRule.objects.all()
	serializer_class = GradeScaleRuleSerializer

class SchoolYearViewSet(viewsets.ModelViewSet):
	queryset = SchoolYear.objects.all()
	serializer_class = SchoolYearSerializer

class MessageToStudentViewSet(viewsets.ModelViewSet):
	queryset = MessageToStudent.objects.all()
	serializer_class = MessageToStudentSerializer
"""
