from rest_framework import serializers
from .models import Document, Certification
from core.validators import validate_no_emoji, validate_no_sql_xss


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    is_expired = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()
    file_size_display = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = [
            "id",
            "vessel",
            "vessel_name",
            "title",
            "document_type",
            "document_number",
            "file",
            "file_size",
            "file_size_display",
            "version",
            "status",
            "description",
            "uploaded_by",
            "uploaded_by_name",
            "expiry_date",
            "tags",
            "is_expired",
            "is_expiring_soon",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uploaded_by", "file_size"]

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}".strip()
        return None

    def validate_title(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Title must be at least 2 characters.")
        return value.strip()

    def validate_file(self, value):
        if value:
            # max 50MB
            max_size = 50 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError("File size cannot exceed 50MB.")

            # allowed file types
            allowed_types = [
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/webp",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/zip",
            ]
            if (
                hasattr(value, "content_type")
                and value.content_type not in allowed_types
            ):
                raise serializers.ValidationError(
                    "Unsupported file type. Allowed: PDF, images, Word, Excel, ZIP."
                )
        return value

    def validate_tags(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value


class CertificationSerializer(serializers.ModelSerializer):
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    days_until_expiry = serializers.ReadOnlyField()

    class Meta:
        model = Certification
        fields = [
            "id",
            "vessel",
            "vessel_name",
            "cert_type",
            "title",
            "cert_number",
            "issuing_body",
            "issued_date",
            "expiry_date",
            "status",
            "file",
            "notes",
            "days_until_expiry",
            "created_at",
            "updated_at",
        ]

    def validate_title(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.strip()

    def validate_cert_number(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.strip()

    def validate(self, data):
        issued_date = data.get("issued_date")
        expiry_date = data.get("expiry_date")
        if issued_date and expiry_date and expiry_date < issued_date:
            raise serializers.ValidationError(
                {"expiry_date": "Expiry date cannot be before issued date."}
            )
        return data
