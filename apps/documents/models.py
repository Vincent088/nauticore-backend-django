from django.db import models
from django.utils import timezone
from core.models import BaseModel
from apps.accounts.models import CustomUser
from apps.vessels.models import Vessel


class Document(BaseModel):

    class DocumentType(models.TextChoices):
        DRAWING = "drawing", "Technical Drawing"
        CERTIFICATE = "certificate", "Certificate"
        REPORT = "report", "Report"
        PHOTO = "photo", "Photo"
        CONTRACT_DOC = "contract_doc", "Contract Document"
        MANUAL = "manual", "Manual"
        INSPECTION = "inspection", "Inspection Report"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"
        EXPIRED = "expired", "Expired"

    vessel = models.ForeignKey(
        Vessel, on_delete=models.CASCADE, related_name="documents"
    )
    title = models.CharField(max_length=200)
    document_type = models.CharField(
        max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER
    )
    document_number = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to="documents/%Y/%m/")
    file_size = models.PositiveIntegerField(default=0, help_text="Size in bytes")
    version = models.CharField(max_length=20, default="1.0")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="documents"
    )
    expiry_date = models.DateField(null=True, blank=True)
    tags = models.CharField(
        max_length=200, blank=True, help_text="Comma separated tags"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.vessel.name})"

    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False

    @property
    def is_expiring_soon(self):
        if self.expiry_date:
            days_left = (self.expiry_date - timezone.now().date()).days
            return 0 <= days_left <= 30
        return False

    @property
    def file_size_display(self):
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, "size"):
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class Certification(BaseModel):

    class CertType(models.TextChoices):
        CLASS = "class", "Class Certificate"
        SAFETY = "safety", "Safety Certificate"
        TONNAGE = "tonnage", "Tonnage Certificate"
        LOAD_LINE = "load_line", "Load Line Certificate"
        ISM = "ism", "ISM Certificate"
        ISPS = "isps", "ISPS Certificate"
        MARPOL = "marpol", "MARPOL Certificate"
        RADIO = "radio", "Radio Certificate"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        VALID = "valid", "Valid"
        EXPIRING_SOON = "expiring_soon", "Expiring Soon"
        EXPIRED = "expired", "Expired"
        SUSPENDED = "suspended", "Suspended"
        REVOKED = "revoked", "Revoked"

    vessel = models.ForeignKey(
        Vessel, on_delete=models.CASCADE, related_name="certifications"
    )
    cert_type = models.CharField(max_length=20, choices=CertType.choices)
    title = models.CharField(max_length=200)
    cert_number = models.CharField(max_length=100, blank=True)
    issuing_body = models.CharField(max_length=200, blank=True)
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.VALID
    )
    file = models.FileField(upload_to="certifications/%Y/%m/", null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["expiry_date"]

    def __str__(self):
        return f"{self.title} ({self.vessel.name})"

    @property
    def days_until_expiry(self):
        if self.expiry_date:
            return (self.expiry_date - timezone.now().date()).days
        return None

    def update_status(self):
        if not self.expiry_date:
            return
        days = self.days_until_expiry
        if days < 0:
            self.status = "expired"
        elif days <= 30:
            self.status = "expiring_soon"
        else:
            self.status = "valid"
        self.save()
