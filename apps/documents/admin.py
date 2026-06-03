from django.contrib import admin
from django.utils.html import format_html
from .models import Document, Certification


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "vessel",
        "document_type",
        "version",
        "status_badge",
        "file_size_display",
        "expiry_date",
        "uploaded_by",
        "created_at",
    ]
    list_filter = ["document_type", "status"]
    search_fields = ["title", "document_number", "vessel__name"]
    readonly_fields = ["id", "file_size", "created_at", "updated_at"]

    def status_badge(self, obj):
        colors = {
            "draft": "#6c757d",
            "active": "#198754",
            "archived": "#0d6efd",
            "expired": "#dc3545",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "vessel",
        "cert_type",
        "cert_number",
        "issuing_body",
        "issued_date",
        "expiry_date",
        "status_badge",
        "days_until_expiry",
    ]
    list_filter = ["cert_type", "status"]
    search_fields = ["title", "cert_number", "vessel__name", "issuing_body"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def status_badge(self, obj):
        colors = {
            "valid": "#198754",
            "expiring_soon": "#ffc107",
            "expired": "#dc3545",
            "suspended": "#fd7e14",
            "revoked": "#6c757d",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"
