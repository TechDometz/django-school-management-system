from django.urls import path, include
from rest_framework.routers import DefaultRouter

from schedule.views import PeriodViewSet, run_generate_timetable

# Initialize the router
router = DefaultRouter()
router.register(r"periods", PeriodViewSet, basename="periods")

urlpatterns = [
    # Include ViewSet routes
    path("", include(router.urls)),
    # Generate timetable endpoint
    path("generate-timetable/", run_generate_timetable, name="generate_timetable"),
]
