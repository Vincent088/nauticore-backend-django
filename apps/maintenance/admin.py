from django.contrib import admin
from django.utils.html import format_html
from .models import (
    MaintenanceType,
    MaintenanceSchedule,
    MaintenancePart,
    ServiceHistory,
)


@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "interval_days", "schedule_count", "created_at"]
    search_fields = ["name"]

    def schedule_count(self, obj):
        return obj.schedules.count()

    schedule_count.short_description = "Schedules"


class MaintenancePartInline(admin.TabularInline):
    model = MaintenancePart
    extra = 0
    fields = ["material", "quantity", "notes"]


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "vessel",
        "maintenance_type",
        "status_badge",
        "priority_badge",
        "scheduled_date",
        "assigned_to",
        "is_overdue",
    ]
    list_filter = ["status", "priority", "maintenance_type"]
    search_fields = ["title", "vessel__name", "vessel__project_number"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [MaintenancePartInline]

    def status_badge(self, obj):
        colors = {
            "scheduled": "#0d6efd",
            "in_progress": "#fd7e14",
            "completed": "#198754",
            "overdue": "#dc3545",
            "cancelled": "#6c757d",
            "postponed": "#ffc107",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def priority_badge(self, obj):
        colors = {
            "low": "#198754",
            "medium": "#0d6efd",
            "high": "#fd7e14",
            "critical": "#dc3545",
        }
        color = colors.get(obj.priority, "#6c757d")
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;'
            'border-radius:4px;font-size:11px">{}</span>',
            color,
            obj.get_priority_display(),
        )

    priority_badge.short_description = "Priority"


@admin.register(ServiceHistory)
class ServiceHistoryAdmin(admin.ModelAdmin):
    list_display = ["title", "vessel", "service_date", "performed_by", "hours_spent"]
    list_filter = ["service_date"]
    search_fields = ["title", "vessel__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
