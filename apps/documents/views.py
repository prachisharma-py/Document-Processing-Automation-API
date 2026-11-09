from django.db import transaction

from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from .models import Document
from .serializers import DocumentUploadSerializer, DocumentTextSerializer
from .tasks import process_document

# Create your views here.


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        document = serializer.save()
        document.status = Document.Status.PENDING
        document.save(update_fields=["status", "updated_at"])

        transaction.on_commit(
            lambda: process_document.delay(document.id)
        )


class DocumentDetailView(generics.RetrieveAPIView):
    serializer_class = DocumentUploadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)


class DocumentDeleteView(generics.DestroyAPIView):
    serializer_class = DocumentUploadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.file:
            instance.file.delete(save=False)

        instance.delete()


class DocumentTextView(generics.RetrieveAPIView):
    serializer_class = DocumentTextSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        document = self.get_object()

        if document.status == Document.Status.FAILED:
            return Response(
                {
                    "detail": "Document processing failed.",
                    "status": document.status,
                },
                status=status.HTTP_409_CONFLICT,
            )

        if document.status != Document.Status.COMPLETED:
            return Response(
                {
                    "detail": "Document processing is not complete yet.",
                    "status": document.status,
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.get_serializer(document)
        return Response(serializer.data)
