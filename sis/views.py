import openpyxl
from django.db.models import Q
from rest_framework import views
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.http import Http404

from academic.models import Student, ClassLevel, Parent
from .serializers import StudentSerializer


class StudentListView(APIView):
    """
    API View for handling single and listing students with pagination and flexible search.
    """

    class StudentPagination(PageNumberPagination):
        page_size = 30  # Default number of students per page
        page_size_query_param = "page_size"  # Allow clients to specify page size
        max_page_size = 100  # Maximum allowed page size

    def get(self, request, format=None):
        # Retrieve search query parameters
        first_name_query = request.query_params.get("first_name", "")
        middle_name_query = request.query_params.get("middle_name", "")
        last_name_query = request.query_params.get("last_name", "")
        class_level_query = request.query_params.get("class_level", "")

        # Start with all students
        students = Student.objects.all()

        # Apply filters dynamically based on provided query parameters
        filters = Q()
        if first_name_query:
            filters &= Q(first_name__icontains=first_name_query)
        if middle_name_query:
            filters &= Q(middle_name__icontains=middle_name_query)
        if last_name_query:
            filters &= Q(last_name__icontains=last_name_query)
        if class_level_query:
            filters &= Q(class_level__icontains=class_level_query)

        # Apply the combined filters to the queryset
        if filters:
            students = students.filter(filters)

        '''
        # Paginate the results
        paginator = self.StudentPagination()
        paginated_students = paginator.paginate_queryset(students, request)
        serializer = StudentSerializer(paginated_students, many=True)
        return paginator.get_paginated_response(serializer.data)
        '''

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        data = request.data
        print(data)
        serializer = StudentSerializer(data=data)
        if serializer.is_valid():
            student = serializer.save()
            return Response(
                StudentSerializer(student).data,
                status=status.HTTP_201_CREATED,
            )
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
                "class_level",
                "gender",
                "date_of_birth",
            ]

            students_to_create = []
            sibling_relationships = []  # To store sibling pairs for linking
            not_created = []  # List to store rows with errors

            for i, row in enumerate(
                sheet.iter_rows(min_row=2, values_only=True), start=2
            ):
                # Map row data to the expected columns
                student_data = dict(zip(columns, row))

                try:
                    # Validate class level
                    try:
                        class_level = ClassLevel.objects.get(
                            name=student_data["class_level"]
                        )
                    except ClassLevel.DoesNotExist:
                        raise ValueError(
                            f"Class level '{student_data['class_level']}' does not exist."
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
                                "email": f"parent_of_{student_data['first_name']}_{student_data['last_name']}@hayatul.com",
                            },
                        )

                    # Check for existing siblings
                    existing_sibling = Student.objects.filter(
                        parent_contact=parent_contact
                    ).first()

                    # Check for duplicate admission number
                    if Student.objects.filter(
                        admission_number=student_data["admission_number"]
                    ).exists():
                        raise ValueError(
                            f"Admission number '{student_data['admission_number']}' already exists."
                        )

                    # Prepare the student instance
                    student = Student(
                        first_name=student_data["first_name"],
                        middle_name=student_data["middle_name"],
                        last_name=student_data["last_name"],
                        admission_number=student_data["admission_number"],
                        parent_contact=parent_contact,
                        region=student_data["region"],
                        city=student_data["city"],
                        class_level=class_level,
                        gender=student_data["gender"],
                        date_of_birth=student_data["date_of_birth"],
                        parent_guardian=parent,  # Assign the parent to the student
                    )
                    students_to_create.append(student)

                    # Store sibling relationships for later processing
                    if existing_sibling:
                        sibling_relationships.append((student, existing_sibling))

                except Exception as e:
                    # Add row data and error message to the not_created list
                    student_data["error"] = str(e)
                    not_created.append(student_data)

            # Bulk create students
            Student.objects.bulk_create(students_to_create)

            # Link sibling relationships
            for new_student, sibling in sibling_relationships:
                new_student.siblings.add(sibling)
                sibling.siblings.add(new_student)

            return Response(
                {
                    "message": f"{len(students_to_create)} students successfully uploaded.",
                    "not_created": not_created,
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
