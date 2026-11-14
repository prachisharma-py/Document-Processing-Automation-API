import logging

from celery import shared_task
from django.db import transaction

from apps.documents.models import Document
from apps.documents.services import extract_text_from_pdf

logger = logging.getLogger(__name__)


@shared_task
def test_celery_task():
    return "Celery is working!"


@shared_task(
        bind=True,
        max_retries=3,
        default_retry_delay=10,
)
def process_document(self, document_id):
    with transaction.atomic():
        try:
            document = (
                Document.objects.select_for_update().get(id=document_id)
            )
        except Document.DoesNotExist:
            return None

        if document.status in {
            Document.Status.PROCESSING,
            Document.Status.COMPLETED,
        }:
            return None

        logger.info(
            "Document processing started",
            extra={"document_id": document_id}
        )

        document.status = Document.Status.PROCESSING
        document.extracted_text = ""
        document.processing_error = ""

        document.save(
            update_fields=[
                "status",
                "extracted_text",
                "processing_error",
                "updated_at",
            ]
        )

    try:
        with document.file.open("rb") as pdf_file:
            extracted_text = extract_text_from_pdf(pdf_file)

        document.extracted_text = extracted_text
        document.status = Document.Status.COMPLETED
        document.processing_error = ""
        document.save(
            update_fields=["extracted_text", "status", "processing_error", "updated_at",]
        )

        logger.info(
            "Document processing completed",
            extra={
                "document_id": document_id,
                "extracted_text_length": len(extracted_text),
            },
        )

        return {
            "document_id": document.id,
            "status": document.status,
            "extracted_text_length": len(extracted_text),
        }
    
    except FileNotFoundError as exc:
        logger.exception(
            "Document file not found",
            extra={"document_id": document_id},
        )

        document.status = Document.Status.FAILED
        document.processing_error = str(exc)
        document.save(
            update_fields=["status", "processing_error", "updated_at"]
        )
        raise

    except Exception as exc:
        logger.exception(
            "Document processing failed",
            extra={
                "document_id": document_id,
                "retry_count": self.request.retries,
            },
        )

        document.processing_error = str(exc)
        if self.request.retries >= self.max_retries:
            logger.error(
                "Document processing retries exhausted",
                extra={
                    "document_id": document_id,
                    "retry_count": self.request.retries,
                },
            )

            document.status = Document.Status.FAILED
            document.save(
                update_fields=["status", "processing_error", "updated_at"]
            )
            raise

        logger.warning(
            "Scheduling document processing retry",
            extra={
                "document_id": document_id,
                "retry_count": self.request.retries + 1,
            },
        )

        document.status = Document.Status.PENDING
        document.save(
            update_fields=["status", "processing_error", "updated_at"]
        )
        raise self.retry(exc=exc)
