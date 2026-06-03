from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ["description", "quantity", "unit", "unit_price", "total_price"]
    readonly_fields = ["total_price"]


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ["payment_method", "amount", "payment_date", "status", "reference"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "contract",
        "status_badge",
        "currency",
        "total_amount",
        "amount_paid",
        "due_date",
        "is_overdue",
        "created_at",
    ]
    list_filter = ["status", "currency"]
    search_fields = ["invoice_number", "contract__client__name"]
    readonly_fields = [
        "id",
        "subtotal",
        "tax_amount",
        "total_amount",
        "amount_paid",
        "created_at",
        "updated_at",
    ]
    inlines = [InvoiceItemInline, PaymentInline]

    fieldsets = (
        ("Invoice Info", {"fields": ("id", "invoice_number", "contract", "status")}),
        (
            "Financial",
            {
                "fields": (
                    "currency",
                    "subtotal",
                    "tax_rate",
                    "tax_amount",
                    "discount",
                    "total_amount",
                    "amount_paid",
                )
            },
        ),
        ("Dates", {"fields": ("issue_date", "due_date", "paid_date")}),
        ("Notes", {"fields": ("notes",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def status_badge(self, obj):
        colors = {
            "draft": "#6c757d",
            "sent": "#0d6efd",
            "partially_paid": "#fd7e14",
            "paid": "#198754",
            "overdue": "#dc3545",
            "cancelled": "#adb5bd",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "invoice",
        "payment_method",
        "amount",
        "payment_date",
        "status",
        "reference",
        "confirmed_by",
    ]
    list_filter = ["status", "payment_method"]
    search_fields = ["invoice__invoice_number", "reference"]
    readonly_fields = ["id", "created_at", "updated_at"]
