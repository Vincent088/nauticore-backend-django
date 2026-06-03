import uuid
from django.db import models
from core.models import BaseModel
from apps.accounts.models import CustomUser
from apps.clients.models import Client
from apps.vessels.models import Vessel


class Contract(BaseModel):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        SUSPENDED = "suspended", "Suspended"

    class Currency(models.TextChoices):
        USD = "USD", "US Dollar"
        IDR = "IDR", "Indonesian Rupiah"
        SGD = "SGD", "Singapore Dollar"
        EUR = "EUR", "Euro"
        GBP = "GBP", "British Pound"

    contract_number = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=200)
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="contracts"
    )
    vessel = models.OneToOneField(
        Vessel, on_delete=models.PROTECT, related_name="contract", null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    currency = models.CharField(
        max_length=5, choices=Currency.choices, default=Currency.USD
    )
    total_value = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    signed_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="contracts_created",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.contract_number} — {self.title}"

    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments.filter(status="confirmed"))

    @property
    def outstanding_balance(self):
        return self.total_value - self.total_paid


class ContractTerm(BaseModel):
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="contract_terms"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} ({self.contract.contract_number})"


class PaymentSchedule(BaseModel):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DUE = "due", "Due"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="payment_schedules"
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.title} — {self.amount} ({self.contract.contract_number})"

    @property
    def is_overdue(self):
        from django.utils import timezone

        if self.status == "pending" and self.due_date:
            return timezone.now().date() > self.due_date
        return False
