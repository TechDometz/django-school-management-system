from django.urls import path
from academic.views import SubjectListView, BulkUploadSubjectsView

urlpatterns = [
    path("subjects/", SubjectListView.as_view(), name="subject-list"),
    path(
        "subjects/bulk-upload/",
        BulkUploadSubjectsView.as_view(),
        name="subject-bulk-upload",
    ),
]
