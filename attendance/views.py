from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from .models import TeachersAttendance, StudentAttendance, PeriodAttendance
from .serializers import (
    TeacherAttendanceSerializer,
    StudentAttendanceSerializer,
    PeriodAttendanceSerializer,
)


class TeacherAttendanceListView(APIView):

    queryset = TeachersAttendance.objects.all()
    serializer_class = TeacherAttendanceSerializer
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ["teacher__fname", "date"]

    def get(self, request):
        attendances = TeachersAttendance.objects.all()
        serializer = TeacherAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TeacherAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherAttendanceDetailView(APIView):
    def get(self, request, pk):
        try:
            attendance = TeachersAttendance.objects.get(pk=pk)
        except TeachersAttendance.DoesNotExist:
            raise NotFound(detail="Teacher Attendance record not found.")

        serializer = TeacherAttendanceSerializer(attendance)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            attendance = TeachersAttendance.objects.get(pk=pk)
        except TeachersAttendance.DoesNotExist:
            raise NotFound(detail="Teacher Attendance record not found.")

        serializer = TeacherAttendanceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            attendance = TeachersAttendance.objects.get(pk=pk)
        except TeachersAttendance.DoesNotExist:
            raise NotFound(detail="Teacher Attendance record not found.")

        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentAttendanceListView(APIView):
    def get(self, request):
        attendances = StudentAttendance.objects.all()
        serializer = StudentAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StudentAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentAttendanceDetailView(APIView):
    def get(self, request, pk):
        try:
            attendance = StudentAttendance.objects.get(pk=pk)
        except StudentAttendance.DoesNotExist:
            raise NotFound(detail="Student Attendance record not found.")

        serializer = StudentAttendanceSerializer(attendance)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            attendance = StudentAttendance.objects.get(pk=pk)
        except StudentAttendance.DoesNotExist:
            raise NotFound(detail="Student Attendance record not found.")

        serializer = StudentAttendanceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            attendance = StudentAttendance.objects.get(pk=pk)
        except StudentAttendance.DoesNotExist:
            raise NotFound(detail="Student Attendance record not found.")

        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PeriodAttendanceListView(APIView):
    def get(self, request):
        attendances = PeriodAttendance.objects.all()
        serializer = PeriodAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PeriodAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PeriodAttendanceDetailView(APIView):
    def get(self, request, pk):
        try:
            attendance = PeriodAttendance.objects.get(pk=pk)
        except PeriodAttendance.DoesNotExist:
            raise NotFound(detail="Period Attendance record not found.")

        serializer = PeriodAttendanceSerializer(attendance)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            attendance = PeriodAttendance.objects.get(pk=pk)
        except PeriodAttendance.DoesNotExist:
            raise NotFound(detail="Period Attendance record not found.")

        serializer = PeriodAttendanceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            attendance = PeriodAttendance.objects.get(pk=pk)
        except PeriodAttendance.DoesNotExist:
            raise NotFound(detail="Period Attendance record not found.")

        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
