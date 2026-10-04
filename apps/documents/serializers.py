from rest_framework import serializers
from .models import Document


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "file",
            "original_filename",
            "file_type",
            "file_size",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "original_filename",
            "file_type",
            "file_size",
            "status",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        uploaded_file = validated_data["file"]

        validated_data["original_filename"] = uploaded_file.name
        validated_data["file_type"] = (
            uploaded_file.name.rsplit(".", 1)[-1].lower()
            if "." in uploaded_file.name
            else ""
        )
        validated_data["file_size"] = uploaded_file.size
        validated_data["user"] = self.context["request"].user

        return super().create(validated_data)
        