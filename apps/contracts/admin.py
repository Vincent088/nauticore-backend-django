from django.contrib import admin
from django.utils.html import format_html
from .models import Contract, ContractTerm, PaymentSchedule


class ContractTermInline(admin.TabularInline):
    model = ContractTerm
    extra = 0
    fields = ["order", "title", "description"]


class PaymentScheduleInline(admin.TabularInline):
    model = PaymentSchedule
    extra = 0
    fields = ["title", "amount", "due_date", "status"]


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = [
        "contract_number",
        "title",
        "client",
        "vessel",
        "status_badge",
        "currency",
        "total_value",
        "end_date",
        "created_at",
    ]
    list_filter = ["status", "currency"]
    search_fields = ["contract_number", "title", "client__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [ContractTermInline, PaymentScheduleInline]

    fieldsets = (
        ("Contract Info", {"fields": ("id", "contract_number", "title", "status")}),
        ("Parties", {"fields": ("client", "vessel", "created_by")}),
        ("Financial", {"fields": ("currency", "total_value")}),
        ("Timeline", {"fields": ("signed_date", "start_date", "end_date")}),
        ("Details", {"fields": ("description", "terms", "notes")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def status_badge(self, obj):
        colors = {
            "draft": "#6c757d",
            "active": "#198754",
            "completed": "#0d6efd",
            "cancelled": "#dc3545",
            "suspended": "#ffc107",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ["title", "contract", "amount", "due_date", "status"]
    list_filter = ["status"]
    search_fields = ["title", "contract__contract_number"]
