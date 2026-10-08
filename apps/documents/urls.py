from django.urls import path

from .views import DocumentListCreateView, DocumentDetailView, DocumentDeleteView


urlpatterns = [
    path("", DocumentListCreateView.as_view(), name="document-list-create"),
    path("<int:pk>/", DocumentDetailView.as_view(), name="document-detail"),
    path("<int:pk>/delete/", DocumentDeleteView.as_view(), name="document-delete"),
]
