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

    def validate_file(self, uploaded_file):
        if not uploaded_file.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Only PDF files are allowed."
            )

        max_size = 10 * 1024 * 1024     

        if uploaded_file.size > max_size:
            raise serializers.ValidationError(
                "Fiile size must not exceed 10 MB."
            )

        return uploaded_file
    

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
        