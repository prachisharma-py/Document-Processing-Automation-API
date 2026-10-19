import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.documents.models import Document
from apps.documents.tasks import process_document

from celery.exceptions import Retry


User = get_user_model()


class DocumentProcessingTasksTests(TestCase):
    def setUp(self):
        self.temp_media = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=self.temp_media.name
        )
        self.settings_override.enable()
        self.addCleanup(self.temp_media.cleanup)
        self.addCleanup(self.settings_override.disable)

        self.user = User.objects.create_user(
            email="processor@example.com",
            password="testpassword123",
        )

        self.document = Document.objects.create(
            user=self.user,
            title="test Document",
            file=SimpleUploadedFile(
                "test.pdf",
                b"test PDF content",
                content_type="application/pdf",
            ),
            original_filename="test.pdf",
            file_type="pdf",
            file_size=16,
        )


    @patch(
        "apps.documents.tasks.extract_text_from_pdf",
        return_value="Extracted PDF text",

    )
    def test_process_document_success(self, mock_extract):
        result = process_document(self.document.id)

        self.document.refresh_from_db()

        self.assertEqual(self.document.status, Document.Status.COMPLETED)
        self.assertEqual(
            self.document.extracted_text,
            "Extracted PDF text",
        )
        self.assertEqual(self.document.processing_error, "")
        self.assertEqual(result["document_id"], self.document.id)
        self.assertEqual(result["extracted_text_length"], 18)
        mock_extract.assert_called_once_with(self.document.file.path)


    @patch(
        "apps.documents.tasks.extract_text_from_pdf",
        side_effect=RuntimeError("Temporary PDF processing error"),
    )
    @patch(
        "apps.documents.tasks.process_document.retry",
        side_effect=Retry("Retrying PDF processing"),
    )
    def test_process_document_retries_on_failure(
        self, mock_retry, mock_extract
    ):
        with self.assertRaises(Retry):
            process_document.run(self.document.id)

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.status,
            Document.Status.PROCESSING,
        )
        self.assertEqual(
            self.document.processing_error,
            "Temporary PDF processing error",
        )
        mock_extract.assert_called_once_with(self.document.file.path)
        mock_retry.assert_called_once()


    @patch(
        "apps.documents.tasks.extract_text_from_pdf",
        side_effect=RuntimeError("PDF processing failed"),
    )
    def test_process_document_marks_failed_after_retries_exhausted(
        self, mock_extract
    ):
        request_context = type(
            "Request",
            (),
            {"retries": process_document.max_retries},
        )()

        process_document.request_stack.push(request_context)
        try:
            with self.assertRaises(RuntimeError):
                process_document.run(self.document.id)
        finally:
            process_document.request_stack.pop()

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.status,
            Document.Status.FAILED,
        )
        self.assertEqual(
            self.document.processing_error,
            "PDF processing failed",
        )


    @patch(
        "apps.documents.tasks.extract_text_from_pdf",
        side_effect=FileNotFoundError("PDF file not found: test.pdf"),
    )
    @patch(
        "apps.documents.tasks.process_document.retry"
    )
    def test_process_document_marks_failed_when_file_is_missing(
        self, mock_retry, mock_extract
    ):
        with self.assertRaises(FileNotFoundError):
            process_document.run(self.document.id)

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.status,
            Document.Status.FAILED,
        )

        self.assertEqual(
            self.document.processing_error,
            "PDF file not found: test.pdf",
        )

        mock_extract.assert_called_once_with(self.document.file.path)
        mock_retry.assert_not_called()


    def test_process_document_handles_deleted_document(self):
        document_id = self.document.id
        self.document.delete()

        result = process_document.run(document_id)

        self.assertIsNone(result)


    @patch(
        "apps.documents.tasks.extract_text_from_pdf",
        return_value="Extracted PDF text",
    )
    def test_process_document_can_run_twice(self, mock_extract):
        first_result = process_document.run(self.document.id)
        second_result = process_document.run(self.document.id)

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.status,
            Document.Status.COMPLETED,
        )
        self.assertEqual(
            self.document.extracted_text,
            "Extracted PDF text",
        )
        self.assertEqual(first_result, second_result)
        self.assertEqual(mock_extract.call_count, 2)
