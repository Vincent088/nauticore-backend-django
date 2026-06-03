from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel
from apps.accounts.models import CustomUser
from apps.contracts.models import Contract


class Invoice(BaseModel):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    class Currency(models.TextChoices):
        USD = "USD", "US Dollar"
        IDR = "IDR", "Indonesian Rupiah"
        SGD = "SGD", "Singapore Dollar"
        EUR = "EUR", "Euro"
        GBP = "GBP", "British Pound"

    invoice_number = models.CharField(max_length=30, unique=True)
    contract = models.ForeignKey(
        Contract, on_delete=models.PROTECT, related_name="invoices"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    currency = models.CharField(
        max_length=5, choices=Currency.choices, default=Currency.USD
    )
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Tax percentage e.g. 11 for 11%",
    )
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    issue_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="invoices_created",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.invoice_number} — {self.contract.client.name}"

    @property
    def outstanding_balance(self):
        return self.total_amount - self.amount_paid

    @property
    def is_overdue(self):
        from django.utils import timezone

        if self.due_date and self.status not in ["paid", "cancelled"]:
            return timezone.now().date() > self.due_date
        return False

    def calculate_totals(self):
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total_amount = self.subtotal + self.tax_amount - self.discount
        self.save()

    def update_payment_status(self):
        if self.amount_paid <= 0:
            if self.status not in ["draft", "sent", "cancelled"]:
                self.status = "sent"
        elif self.amount_paid >= self.total_amount:
            self.status = "paid"
            from django.utils import timezone

            self.paid_date = timezone.now().date()
        else:
            self.status = "partially_paid"
        self.save()


class InvoiceItem(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    unit = models.CharField(max_length=20, default="pcs")
    unit_price = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0)]
    )
    total_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.description} ({self.invoice.invoice_number})"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.invoice.calculate_totals()


class Payment(BaseModel):

    class PaymentMethod(models.TextChoices):
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CASH = "cash", "Cash"
        CHEQUE = "cheque", "Cheque"
        LC = "lc", "Letter of Credit"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        REJECTED = "rejected", "Rejected"
        REFUNDED = "refunded", "Refunded"

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payments"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER,
    )
    amount = models.DecimalField(
        max_digits=18, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    payment_date = models.DateField()
    reference = models.CharField(
        max_length=100, blank=True, help_text="Bank reference, cheque number, etc"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    notes = models.TextField(blank=True)
    confirmed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_payments",
    )
    receipt_file = models.FileField(upload_to="receipts/%Y/%m/", null=True, blank=True)

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == "confirmed":
            invoice = self.invoice
            invoice.amount_paid = sum(
                p.amount for p in invoice.payments.filter(status="confirmed")
            )
            invoice.save()
            invoice.update_payment_status()
