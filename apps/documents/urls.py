from django.urls import path

from .views import DocumentUploadedView


urlpatterns = [
    path("upload/", DocumentUploadedView.as_view(), name="document-upload"),
]
