from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel
from apps.accounts.models import CustomUser
from apps.vessels.models import Vessel
from apps.materials.models import Material


class MaintenanceType(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    interval_days = models.PositiveIntegerField(
        default=90, help_text="Default interval in days between maintenance"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MaintenanceSchedule(BaseModel):

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"
        POSTPONED = "postponed", "Postponed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    vessel = models.ForeignKey(
        Vessel, on_delete=models.CASCADE, related_name="maintenance_schedules"
    )
    maintenance_type = models.ForeignKey(
        MaintenanceType, on_delete=models.SET_NULL, null=True, related_name="schedules"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_assignments",
    )
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    actual_hours = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    findings = models.TextField(blank=True, help_text="Issues found during maintenance")

    class Meta:
        ordering = ["scheduled_date"]

    def __str__(self):
        return f"{self.title} — {self.vessel.name} ({self.scheduled_date})"

    @property
    def is_overdue(self):
        from django.utils import timezone

        if self.status == "scheduled" and self.scheduled_date:
            return timezone.now().date() > self.scheduled_date
        return False

    @property
    def days_until_due(self):
        from django.utils import timezone

        if self.scheduled_date:
            return (self.scheduled_date - timezone.now().date()).days
        return None


class MaintenancePart(BaseModel):
    maintenance = models.ForeignKey(
        MaintenanceSchedule, on_delete=models.CASCADE, related_name="parts_used"
    )
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name="maintenance_uses"
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.material.name} x{self.quantity} ({self.maintenance.title})"


class ServiceHistory(BaseModel):
    vessel = models.ForeignKey(
        Vessel, on_delete=models.CASCADE, related_name="service_history"
    )
    maintenance = models.ForeignKey(
        MaintenanceSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_records",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    service_date = models.DateField()
    performed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="service_history"
    )
    hours_spent = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    parts_replaced = models.TextField(blank=True, help_text="List of parts replaced")
    findings = models.TextField(blank=True)
    next_service_date = models.DateField(null=True, blank=True)
    attachments = models.FileField(
        upload_to="service_history/%Y/%m/", null=True, blank=True
    )

    class Meta:
        ordering = ["-service_date"]

    def __str__(self):
        return f"{self.title} — {self.vessel.name} ({self.service_date})"
