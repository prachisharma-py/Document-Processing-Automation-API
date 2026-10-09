from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Document

# Create your tests here.

User = get_user_model()


class DocumentValidationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",
        )

        self.client.force_authenticate(user=self.user)
        self.url = "/api/v1/documents/"


    def create_pdf(self, size=1024):
        content = b"%PDF-1.4\n" + b"A" * size
        return SimpleUploadedFile(
            "test.pdf",
            content,
            content_type="application/pdf",
        )


    def test_valid_pdf_upload(self):
        pdf = self.create_pdf()

        response = self.client.post(
            self.url,
            {
                "title": "Test PDF",
                "file": pdf,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.first().file_type, "pdf")


    def test_reject_non_pdf_upload(self):
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not a PDF file.",
            content_type="text/plain",
        )

        response = self.client.post(
            self.url,
            {
                "title": "Invalid Document",
                "file": invalid_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST),
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual("Only PDF files are allowed.", str(response.data["file"][0]))


    def test_reject_oversized_pdf_upload(self):
        oversized_pdf = self.create_pdf(size=10 * 1024 * 1024)
        response = self.client.post(
            self.url,
            {
                "title": "Oversized PDF",
                "file": oversized_pdf,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual("File size must not exceed 10 MB.", str(response.data["file"][0]))
