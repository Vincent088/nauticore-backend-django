import uuid
from django.db import models
from core.models import BaseModel


class Client(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        PROSPECT = "prospect", "Prospect"

    class Industry(models.TextChoices):
        SHIPPING = "shipping", "Shipping"
        OIL_GAS = "oil_gas", "Oil & Gas"
        MILITARY = "military", "Military"
        FISHING = "fishing", "Fishing"
        TOURISM = "tourism", "Tourism"
        GOVERNMENT = "government", "Government"
        OTHER = "other", "Other"

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    industry = models.CharField(
        max_length=20, choices=Industry.choices, default=Industry.OTHER
    )
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class ClientContact(BaseModel):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="contacts"
    )
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "name"]

    def __str__(self):
        return f"{self.name} ({self.client.name})"
