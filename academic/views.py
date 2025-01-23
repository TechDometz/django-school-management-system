import openpyxl
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Subject, Department
from .serializers import SubjectSerializer


class SubjectListView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class BulkUploadSubjectsView(APIView):
    """
    API View to handle bulk uploading of subjects from an Excel file.
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
                "name",  # Subject name
                "subject_code",  # Subject code
                "department",  # Department name (for ForeignKey)
            ]

            subjects_to_create = []
            for i, row in enumerate(
                sheet.iter_rows(min_row=2, values_only=True), start=2
            ):
                # Map row data to the expected columns
                subject_data = dict(zip(columns, row))

                # Validate department
                try:
                    department = Department.objects.get(
                        name=subject_data["department"].lower()
                    )
                except Department.DoesNotExist:
                    return Response(
                        {
                            "error": f"Row {i}: Department '{subject_data['department']}' does not exist."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Check for existing subject based on subject code or name
                if Subject.objects.filter(
                    subject_code=subject_data["subject_code"]
                ).exists():
                    return Response(
                        {
                            "error": f"Row {i}: Subject code '{subject_data['subject_code']}' already exists."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                name = (subject_data["name"],)
                subject_code = (subject_data["subject_code"],)
                # Create Subject object
                subject = Subject(
                    name=subject_data["name"],
                    subject_code=subject_data["subject_code"],
                    description=f"{name} {subject_code}",
                    department=department,
                )
                subjects_to_create.append(subject)

            # Bulk create subjects
            Subject.objects.bulk_create(subjects_to_create)

            return Response(
                {
                    "message": f"{len(subjects_to_create)} subjects successfully uploaded."
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
