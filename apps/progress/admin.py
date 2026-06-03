from django.contrib import admin
from django.utils.html import format_html
from .models import Milestone, Task, WorkLog


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ["name", "status", "priority", "completion_pct", "assigned_to", "due_date"]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "vessel",
        "status_badge",
        "completion_pct",
        "assigned_to",
        "target_date",
        "created_at",
    ]
    list_filter = ["status"]
    search_fields = ["name", "vessel__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [TaskInline]

    def status_badge(self, obj):
        colors = {
            "not_started": "#6c757d",
            "in_progress": "#0d6efd",
            "completed": "#198754",
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


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "milestone",
        "status",
        "priority",
        "completion_pct",
        "assigned_to",
        "due_date",
    ]
    list_filter = ["status", "priority"]
    search_fields = ["name", "milestone__name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ["vessel", "task", "logged_by", "date", "hours"]
    list_filter = ["date"]
    search_fields = ["vessel__name", "description"]
    readonly_fields = ["id", "created_at"]
