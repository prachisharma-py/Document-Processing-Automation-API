from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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

    @patch("apps.documents.views.process_document.delay")
    def test_upload_triggers_background_processing(self, mock_process):
        pdf = self.create_pdf()

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                self.url,
                {
                    "title": "Automatic Processing Test",
                    "file": pdf,
                },
                format="multipart",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        document = Document.objects.get(
            title="Automatic Processing Test"
        )

        self.assertEqual(document.status, Document.Status.PENDING)
        mock_process.assert_called_once_with(document.id)


class DocumentTextViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=self.user)
        self.document = Document.objects.create(
            user=self.user,
            title="Test Document",
            file="documents/test.pdf",
            original_filename="test.pdf",
            file_type="pdf",
            file_size=1024,
            status=Document.Status.COMPLETED,
            extracted_text="This is the extracted PDF text.",
        )
        self.url = f"/api/v1/documents/{self.document.id}/text/"


    def test_completed_document_returns_extracted_text(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["extracted_text"],
            "This is the extracted PDF text.",
        )


    def test_pending_document_returns_conflict(self):
        self.document.status = Document.Status.PENDING
        self.document.save(update_fields=["status"])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["status"], Document.Status.PENDING)


    def test_processing_document_returns_conflict(self):
        self.document.status = Document.Status.PROCESSING
        self.document.save(update_fields=["status"])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["status"], Document.Status.PROCESSING)


    def test_failed_document_returns_conflict(self):
        self.document.status = Document.Status.FAILED
        self.document.save(update_fields=["status"])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["detail"], "Document processing failed.")
