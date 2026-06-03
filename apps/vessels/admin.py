from django.contrib import admin
from django.utils.html import format_html
from .models import Vessel, VesselSpec, VesselPart


class VesselSpecInline(admin.StackedInline):
    model = VesselSpec
    extra = 0


class VesselPartInline(admin.TabularInline):
    model = VesselPart
    extra = 0
    fields = ["name", "part_number", "quantity", "unit", "status", "supplier"]


@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = [
        "project_number",
        "name",
        "client",
        "vessel_type",
        "ship_type",
        "status_badge",
        "target_date",
        "overdue_badge",
        "created_at",
    ]
    list_filter = ["status", "vessel_type", "ship_type"]
    search_fields = ["name", "project_number", "client__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [VesselSpecInline, VesselPartInline]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Project Info",
            {"fields": ("id", "project_number", "name", "client", "project_manager")},
        ),
        ("Classification", {"fields": ("vessel_type", "ship_type", "status")}),
        ("Timeline", {"fields": ("start_date", "target_date", "completed_date")}),
        ("Details", {"fields": ("description", "notes")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def status_badge(self, obj):
        colors = {
            "planning": "#6c757d",
            "in_progress": "#0d6efd",
            "testing": "#fd7e14",
            "completed": "#198754",
            "delivered": "#20c997",
            "on_hold": "#ffc107",
            "cancelled": "#dc3545",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def overdue_badge(self, obj):
        if obj.is_overdue:
            return format_html(
                '<span style="background:#dc3545;color:white;padding:3px 8px;'
                'border-radius:4px;font-size:11px">OVERDUE</span>'
            )
        return ""

    overdue_badge.short_description = "Overdue"


@admin.register(VesselPart)
class VesselPartAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "vessel",
        "part_number",
        "quantity",
        "unit",
        "status",
        "supplier",
    ]
    list_filter = ["status"]
    search_fields = ["name", "part_number", "vessel__name", "supplier"]
