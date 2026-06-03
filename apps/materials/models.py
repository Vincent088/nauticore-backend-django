from django.db import models
from core.models import BaseModel
from apps.accounts.models import CustomUser
from apps.vessels.models import Vessel


class MaterialCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default="#6c757d", help_text="Hex color code"
    )

    class Meta:
        verbose_name_plural = "Material Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Material(BaseModel):

    class Unit(models.TextChoices):
        PCS = "pcs", "Pieces"
        KG = "kg", "Kilogram"
        TON = "ton", "Ton"
        METER = "meter", "Meter"
        LITER = "liter", "Liter"
        SET = "set", "Set"
        ROLL = "roll", "Roll"
        BOX = "box", "Box"
        SHEET = "sheet", "Sheet"

    category = models.ForeignKey(
        MaterialCategory, on_delete=models.SET_NULL, null=True, related_name="materials"
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.PCS)
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, blank=True)
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Storage location e.g. Warehouse A, Rack 3",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock

    @property
    def stock_value(self):
        return self.current_stock * self.unit_price


class StockMovement(BaseModel):

    class MovementType(models.TextChoices):
        IN = "in", "Stock In"
        OUT = "out", "Stock Out"
        TRANSFER = "transfer", "Transfer"
        ADJUST = "adjust", "Adjustment"
        RETURN = "return", "Return"

    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name="movements"
    )
    vessel = models.ForeignKey(
        Vessel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="material_movements",
    )
    movement_type = models.CharField(max_length=10, choices=MovementType.choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reference = models.CharField(
        max_length=100, blank=True, help_text="PO number, invoice number, etc"
    )
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="stock_movements"
    )
    movement_date = models.DateField()

    class Meta:
        ordering = ["-movement_date", "-created_at"]

    def __str__(self):
        return f"{self.movement_type} — {self.material.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        # auto update stock when movement saved
        if not self.pk:
            if self.movement_type == "in" or self.movement_type == "return":
                self.material.current_stock += self.quantity
            elif self.movement_type in ["out", "transfer"]:
                self.material.current_stock -= self.quantity
            elif self.movement_type == "adjust":
                self.material.current_stock = self.quantity
            self.material.save()
        super().save(*args, **kwargs)


class MaterialRequest(BaseModel):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"

    vessel = models.ForeignKey(
        Vessel, on_delete=models.CASCADE, related_name="material_requests"
    )
    material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name="requests"
    )
    requested_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="material_requests",
    )
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_requests",
    )
    quantity_needed = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    needed_by = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.material.name} x{self.quantity_needed} for {self.vessel.name}"
