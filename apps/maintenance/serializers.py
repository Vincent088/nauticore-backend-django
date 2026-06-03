from rest_framework import serializers
from django.utils import timezone
from .models import (
    MaintenanceType,
    MaintenanceSchedule,
    MaintenancePart,
    ServiceHistory,
)
from core.validators import validate_no_emoji, validate_no_sql_xss


class MaintenanceTypeSerializer(serializers.ModelSerializer):
    schedule_count = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceType
        fields = [
            "id",
            "name",
            "description",
            "interval_days",
            "schedule_count",
            "created_at",
        ]

    def get_schedule_count(self, obj):
        return obj.schedules.count()

    def validate_name(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.strip()

    def validate_interval_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Interval must be greater than 0 days.")
        return value


class MaintenancePartSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source="material.name")
    material_code = serializers.ReadOnlyField(source="material.code")
    material_unit = serializers.ReadOnlyField(source="material.unit")

    class Meta:
        model = MaintenancePart
        fields = [
            "id",
            "material",
            "material_name",
            "material_code",
            "material_unit",
            "quantity",
            "notes",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value


class MaintenanceScheduleListSerializer(serializers.ModelSerializer):
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    vessel_number = serializers.ReadOnlyField(source="vessel.project_number")
    maintenance_type_name = serializers.ReadOnlyField(source="maintenance_type.name")
    assigned_to_name = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()

    class Meta:
        model = MaintenanceSchedule
        fields = [
            "id",
            "vessel",
            "vessel_name",
            "vessel_number",
            "maintenance_type",
            "maintenance_type_name",
            "title",
            "status",
            "priority",
            "scheduled_date",
            "completed_date",
            "next_due_date",
            "assigned_to",
            "assigned_to_name",
            "estimated_hours",
            "is_overdue",
            "days_until_due",
            "created_at",
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
        return None


class MaintenanceScheduleDetailSerializer(serializers.ModelSerializer):
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    maintenance_type_name = serializers.ReadOnlyField(source="maintenance_type.name")
    assigned_to_name = serializers.SerializerMethodField()
    parts_used = MaintenancePartSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()

    class Meta:
        model = MaintenanceSchedule
        fields = [
            "id",
            "vessel",
            "vessel_name",
            "maintenance_type",
            "maintenance_type_name",
            "title",
            "description",
            "status",
            "priority",
            "scheduled_date",
            "completed_date",
            "next_due_date",
            "assigned_to",
            "assigned_to_name",
            "estimated_hours",
            "actual_hours",
            "notes",
            "findings",
            "parts_used",
            "is_overdue",
            "days_until_due",
            "created_at",
            "updated_at",
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
        return None


class MaintenanceScheduleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSchedule
        fields = [
            "vessel",
            "maintenance_type",
            "title",
            "description",
            "status",
            "priority",
            "scheduled_date",
            "completed_date",
            "next_due_date",
            "assigned_to",
            "estimated_hours",
            "actual_hours",
            "notes",
            "findings",
        ]

    def validate_title(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.strip()

    def validate_estimated_hours(self, value):
        if value < 0:
            raise serializers.ValidationError("Estimated hours cannot be negative.")
        return value

    def validate(self, data):
        scheduled_date = data.get("scheduled_date")
        completed_date = data.get("completed_date")
        if scheduled_date and completed_date and completed_date < scheduled_date:
            raise serializers.ValidationError(
                {"completed_date": "Completed date cannot be before scheduled date."}
            )
        return data


class ServiceHistorySerializer(serializers.ModelSerializer):
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceHistory
        fields = [
            "id",
            "vessel",
            "vessel_name",
            "maintenance",
            "title",
            "description",
            "service_date",
            "performed_by",
            "performed_by_name",
            "hours_spent",
            "parts_replaced",
            "findings",
            "next_service_date",
            "attachments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["performed_by"]

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return f"{obj.performed_by.first_name} {obj.performed_by.last_name}".strip()
        return None

    def validate_title(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.strip()

    def validate_hours_spent(self, value):
        if value < 0:
            raise serializers.ValidationError("Hours spent cannot be negative.")
        return value
