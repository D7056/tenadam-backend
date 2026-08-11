from rest_framework import serializers
from causes.models import Cause, CauseDocument

MAX_DOCUMENT_SIZE = 10 * 1024 * 1024 
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}


class CauseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CauseDocument
        fields = ["id", "file", "uploaded_at"]

class CauseSerializer(serializers.ModelSerializer):
    documents = CauseDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Cause
        fields = [
            "id", "category", "name", "tagline", "description", "location",
            "goal_amount", "raised_amount", "approved", "created_at", "documents",
        ]
        read_only_fields = ["raised_amount", "approved", "created_at"]


class CreateCauseSerializer(serializers.ModelSerializer):
    documents = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )

    class Meta:
        model = Cause
        fields = [
            "id", "category", "name", "tagline", "description", "location",
            "goal_amount", "documents",
        ]

    def validate_documents(self, files):
        for f in files:
            if f.size > MAX_DOCUMENT_SIZE:
                raise serializers.ValidationError(
                    f"{f.name} is too large (max 10MB)."
                )
            if f.content_type not in ALLOWED_DOCUMENT_TYPES:
                raise serializers.ValidationError(
                    f"{f.name} must be a PDF, JPEG, or PNG."
                )
        return files

    def create(self, validated_data):
        documents = validated_data.pop("documents", [])
        user = self.context["request"].user
        cause = Cause.objects.create(submitted_by=user, **validated_data)
        for f in documents:
            CauseDocument.objects.create(cause=cause, file=f)
        return cause
