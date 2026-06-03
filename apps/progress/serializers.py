from rest_framework import serializers
from django.utils import timezone
from .models import Milestone, Task, WorkLog
from core.validators import validate_no_emoji, validate_no_sql_xss


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "milestone",
            "name",
            "description",
            "status",
            "priority",
            "completion_pct",
            "assigned_to",
            "assigned_to_name",
            "start_date",
            "due_date",
            "completed_date",
            "notes",
            "is_overdue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["completion_pct"]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
        return None

    def get_is_overdue(self, obj):
        if obj.due_date and obj.status not in ["completed", "cancelled"]:
            return timezone.now().date() > obj.due_date
        return False

    def validate_name(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Task name must be at least 2 characters."
            )
        return value.strip()

    def validate_completion_pct(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Completion percentage must be between 0 and 100."
            )
        return value

    def validate(self, data):
        start_date = data.get("start_date")
        due_date = data.get("due_date")
        if start_date and due_date and due_date < start_date:
            raise serializers.ValidationError(
                {"due_date": "Due date cannot be before start date."}
            )
        return data


class MilestoneListSerializer(serializers.ModelSerializer):
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    assigned_to_name = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Milestone
        fields = [
            "id",
            "vessel",
            "vessel_name",
            "name",
            "status",
            "order",
            "completion_pct",
            "assigned_to",
            "assigned_to_name",
            "start_date",
            "target_date",
            "task_count",
            "is_overdue",
            "created_at",
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
        return None

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_is_overdue(self, obj):
        if obj.target_date and obj.status not in ["completed", "cancelled"]:
            return timezone.now().date() > obj.target_date
        return False


class MilestoneDetailSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Milestone
        fields = [
            "id",
            "vessel",
            "name",
            "description",
            "status",
            "order",
            "completion_pct",
            "assigned_to",
            "assigned_to_name",
            "start_date",
            "target_date",
            "completed_date",
            "tasks",
            "is_overdue",
            "created_at",
            "updated_at",
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
        return None

    def get_is_overdue(self, obj):
        if obj.target_date and obj.status not in ["completed", "cancelled"]:
            return timezone.now().date() > obj.target_date
        return False


class MilestoneWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = [
            "vessel",
            "name",
            "description",
            "status",
            "order",
            "completion_pct",
            "assigned_to",
            "start_date",
            "target_date",
            "completed_date",
        ]

    def validate_name(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.strip()

    def validate_completion_pct(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Completion must be between 0 and 100.")
        return value

    def validate(self, data):
        start_date = data.get("start_date")
        target_date = data.get("target_date")
        if start_date and target_date and target_date < start_date:
            raise serializers.ValidationError(
                {"target_date": "Target date cannot be before start date."}
            )
        return data


class WorkLogSerializer(serializers.ModelSerializer):
    logged_by_name = serializers.SerializerMethodField()
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    task_name = serializers.ReadOnlyField(source="task.name")

    class Meta:
        model = WorkLog
        fields = [
            "id",
            "vessel",
            "vessel_name",
            "task",
            "task_name",
            "logged_by",
            "logged_by_name",
            "date",
            "hours",
            "description",
            "issues",
            "created_at",
        ]
        read_only_fields = ["logged_by"]

    def get_logged_by_name(self, obj):
        if obj.logged_by:
            return f"{obj.logged_by.first_name} {obj.logged_by.last_name}".strip()
        return None

    def validate_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("Hours must be greater than 0.")
        if value > 24:
            raise serializers.ValidationError("Hours cannot exceed 24 per log entry.")
        return value

    def validate_description(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Description must be at least 5 characters."
            )
        return value.strip()
