from celery import shared_task
from django.db import transaction

from apps.documents.models import Document
from apps.documents.services import extract_text_from_pdf


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
        extracted_text = extract_text_from_pdf(document.file.path)

        document.extracted_text = extracted_text
        document.status = Document.Status.COMPLETED
        document.processing_error = ""
        document.save(
            update_fields=["extracted_text", "status", "processing_error", "updated_at",]
        )
        return {
            "document_id": document.id,
            "status": document.status,
            "extracted_text_length": len(extracted_text),
        }
    
    except FileNotFoundError as exc:
        document.status = Document.Status.FAILED
        document.processing_error = str(exc)
        document.save(
            update_fields=["status", "processing_error", "updated_at"]
        )
        raise

    except Exception as exc:
        document.processing_error = str(exc)
        if self.request.retries >= self.max_retries:
            document.status = Document.Status.FAILED
            document.save(
                update_fields=["status", "processing_error", "updated_at"]
            )
            raise

        document.status = Document.Status.PENDING
        document.save(
            update_fields=["status", "processing_error", "updated_at"]
        )
        raise self.retry(exc=exc)
