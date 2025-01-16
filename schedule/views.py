from django.http import JsonResponse
from django.core.management import call_command
from io import StringIO
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Period
from .serializers import PeriodSerializer
from academic.models import AllocatedSubject


class PeriodCreateView(APIView):
    def post(self, request, *args, **kwargs):
        allocated_subject_id = request.data.get("allocated_subject")
        try:
            allocated_subject = AllocatedSubject.objects.get(id=allocated_subject_id)
        except AllocatedSubject.DoesNotExist:
            return Response(
                {"error": "AllocatedSubject not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PeriodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(allocated_subject=allocated_subject)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer


def run_generate_timetable(request):
    """
    View to trigger the timetable generation management command.
    """
    output = StringIO()
    try:
        call_command("generate_timetable", stdout=output)
        return JsonResponse({"status": "success", "message": output.getvalue()})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
