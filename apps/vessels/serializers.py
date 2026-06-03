from rest_framework import serializers
from .models import Vessel, VesselSpec, VesselPart
from apps.clients.serializers import ClientListSerializer
from apps.accounts.serializers import UserSerializer
from core.validators import validate_no_emoji, validate_no_sql_xss


class VesselSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = VesselSpec
        fields = [
            "id",
            "length",
            "beam",
            "draft",
            "gross_ton",
            "deadweight",
            "engine_type",
            "horsepower",
            "speed",
            "capacity",
            "material",
            "class_notation",
        ]

    def validate_length(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("Length must be greater than 0.")
        if value and value > 500:
            raise serializers.ValidationError("Length cannot exceed 500 meters.")
        return value

    def validate_horsepower(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("Horsepower must be greater than 0.")
        return value

    def validate_speed(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("Speed must be greater than 0.")
        if value and value > 100:
            raise serializers.ValidationError("Speed cannot exceed 100 knots.")
        return value


class VesselPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = VesselPart
        fields = [
            "id",
            "name",
            "part_number",
            "description",
            "quantity",
            "unit",
            "status",
            "supplier",
            "notes",
            "created_at",
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_name(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value


class VesselListSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source="client.name")
    manager_name = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    completion_pct = serializers.SerializerMethodField()

    class Meta:
        model = Vessel
        fields = [
            "id",
            "project_number",
            "name",
            "client_name",
            "manager_name",
            "vessel_type",
            "ship_type",
            "status",
            "start_date",
            "target_date",
            "is_overdue",
            "completion_pct",
            "created_at",
        ]

    def get_manager_name(self, obj):
        if obj.project_manager:
            return f"{obj.project_manager.first_name} {obj.project_manager.last_name}".strip()
        return None

    def get_completion_pct(self, obj):
        milestones = obj.milestones.all() if hasattr(obj, "milestones") else []
        if not milestones:
            return 0
        total = sum(m.completion_pct for m in milestones)
        return round(total / len(milestones), 1)


class VesselDetailSerializer(serializers.ModelSerializer):
    client = ClientListSerializer(read_only=True)
    project_manager = UserSerializer(read_only=True)
    spec = VesselSpecSerializer(read_only=True)
    parts = VesselPartSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    completion_pct = serializers.SerializerMethodField()
    parts_count = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()

    class Meta:
        model = Vessel
        fields = [
            "id",
            "project_number",
            "name",
            "client",
            "project_manager",
            "vessel_type",
            "ship_type",
            "status",
            "start_date",
            "target_date",
            "completed_date",
            "description",
            "notes",
            "spec",
            "parts",
            "is_overdue",
            "completion_pct",
            "parts_count",
            "documents_count",
            "created_at",
            "updated_at",
        ]

    def get_completion_pct(self, obj):
        milestones = obj.milestones.all() if hasattr(obj, "milestones") else []
        if not milestones:
            return 0
        total = sum(m.completion_pct for m in milestones)
        return round(total / len(milestones), 1)

    def get_parts_count(self, obj):
        return obj.parts.count()

    def get_documents_count(self, obj):
        return obj.documents.count() if hasattr(obj, "documents") else 0


class VesselWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vessel
        fields = [
            "project_number",
            "name",
            "client",
            "project_manager",
            "vessel_type",
            "ship_type",
            "status",
            "start_date",
            "target_date",
            "completed_date",
            "description",
            "notes",
        ]

    def validate_project_number(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        if not value.strip():
            raise serializers.ValidationError("Project number cannot be empty.")
        return value.upper().strip()

    def validate_name(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Vessel name must be at least 2 characters."
            )
        return value.strip()

    def validate(self, data):
        start_date = data.get("start_date")
        target_date = data.get("target_date")
        if start_date and target_date and target_date < start_date:
            raise serializers.ValidationError(
                {"target_date": "Target date cannot be before start date."}
            )
        return data
