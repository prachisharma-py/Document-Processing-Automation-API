from django.db import models
from django.conf import settings

# Create your models here.


class Document(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded",
        PENDING = "PENDING", "Pending",
        PROCESSING = "PROCESSING", "Processing",
        COMPLETED = "COMPLETED", "Completed",
        FAILED = "FAILED", "Failed",

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    title = models.CharField(
        max_length=255
    )
    file = models.FileField(
        upload_to="documents/"
    )
    original_filename = models.CharField(
        max_length=255
    )
    file_type = models.CharField(
        max_length=50
    )
    file_size = models.PositiveBigIntegerField(
        default=0
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title
