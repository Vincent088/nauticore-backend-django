import uuid
from django.db import models
from core.models import BaseModel
from apps.accounts.models import CustomUser
from apps.clients.models import Client


class Vessel(BaseModel):

    class VesselType(models.TextChoices):
        NEW_BUILD = "new_build", "New Build"
        REPAIR = "repair", "Repair"
        MAINTENANCE = "maintenance", "Maintenance"
        CONVERSION = "conversion", "Conversion"

    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        IN_PROGRESS = "in_progress", "In Progress"
        TESTING = "testing", "Testing"
        COMPLETED = "completed", "Completed"
        DELIVERED = "delivered", "Delivered"
        ON_HOLD = "on_hold", "On Hold"
        CANCELLED = "cancelled", "Cancelled"

    class ShipType(models.TextChoices):
        TUGBOAT = "tugboat", "Tugboat"
        CARGO = "cargo", "Cargo Ship"
        TANKER = "tanker", "Tanker"
        BARGE = "barge", "Barge"
        FERRY = "ferry", "Ferry"
        FISHING = "fishing", "Fishing Vessel"
        PATROL = "patrol", "Patrol Boat"
        DREDGER = "dredger", "Dredger"
        OTHER = "other", "Other"

    project_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="vessels")
    project_manager = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="managed_vessels"
    )
    vessel_type = models.CharField(max_length=20, choices=VesselType.choices)
    ship_type = models.CharField(
        max_length=20, choices=ShipType.choices, default=ShipType.OTHER
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNING
    )
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project_number} — {self.name}"

    @property
    def is_overdue(self):
        from django.utils import timezone

        if self.target_date and self.status not in [
            "completed",
            "delivered",
            "cancelled",
        ]:
            return timezone.now().date() > self.target_date
        return False


class VesselSpec(BaseModel):
    vessel = models.OneToOneField(Vessel, on_delete=models.CASCADE, related_name="spec")
    length = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, help_text="meters"
    )
    beam = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, help_text="meters"
    )
    draft = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, help_text="meters"
    )
    gross_ton = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    deadweight = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    engine_type = models.CharField(max_length=100, blank=True)
    horsepower = models.IntegerField(null=True, blank=True)
    speed = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, help_text="knots"
    )
    capacity = models.CharField(max_length=100, blank=True)
    material = models.CharField(
        max_length=100, blank=True, help_text="e.g. Steel, Aluminum, Fiberglass"
    )
    class_notation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Spec for {self.vessel.name}"


class VesselPart(BaseModel):
    class PartStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        ORDERED = "ordered", "Ordered"
        RECEIVED = "received", "Received"
        INSTALLED = "installed", "Installed"
        REJECTED = "rejected", "Rejected"

    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name="parts")
    name = models.CharField(max_length=200)
    part_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=20, default="pcs")
    status = models.CharField(
        max_length=20, choices=PartStatus.choices, default=PartStatus.PENDING
    )
    supplier = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.vessel.name})"
