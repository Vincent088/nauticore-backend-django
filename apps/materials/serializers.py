from rest_framework import serializers
from .models import MaterialCategory, Material, StockMovement, MaterialRequest
from core.validators import validate_no_emoji, validate_no_sql_xss


class MaterialCategorySerializer(serializers.ModelSerializer):
    material_count = serializers.SerializerMethodField()

    class Meta:
        model = MaterialCategory
        fields = ["id", "name", "description", "color", "material_count", "created_at"]

    def get_material_count(self, obj):
        return obj.materials.count()

    def validate_name(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value

    def validate_color(self, value):
        import re

        if not re.match(r"^#[0-9A-Fa-f]{6}$", value):
            raise serializers.ValidationError(
                "Color must be a valid hex code e.g. #FF5733"
            )
        return value


class MaterialListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    is_low_stock = serializers.ReadOnlyField()
    stock_value = serializers.ReadOnlyField()

    class Meta:
        model = Material
        fields = [
            "id",
            "code",
            "name",
            "category_name",
            "unit",
            "current_stock",
            "minimum_stock",
            "unit_price",
            "stock_value",
            "is_low_stock",
            "supplier",
            "location",
            "created_at",
        ]


class MaterialDetailSerializer(serializers.ModelSerializer):
    category = MaterialCategorySerializer(read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    stock_value = serializers.ReadOnlyField()

    class Meta:
        model = Material
        fields = [
            "id",
            "code",
            "name",
            "category",
            "description",
            "unit",
            "current_stock",
            "minimum_stock",
            "unit_price",
            "stock_value",
            "is_low_stock",
            "supplier",
            "location",
            "notes",
            "created_at",
            "updated_at",
        ]


class MaterialWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = [
            "code",
            "name",
            "category",
            "description",
            "unit",
            "minimum_stock",
            "unit_price",
            "supplier",
            "location",
            "notes",
        ]

    def validate_code(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.upper().strip()

    def validate_name(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        return value.strip()

    def validate_minimum_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Minimum stock cannot be negative.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        return value


class StockMovementSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source="material.name")
    material_code = serializers.ReadOnlyField(source="material.code")
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "material",
            "material_name",
            "material_code",
            "vessel",
            "vessel_name",
            "movement_type",
            "quantity",
            "unit_price",
            "reference",
            "notes",
            "performed_by",
            "performed_by_name",
            "movement_date",
            "created_at",
        ]
        read_only_fields = ["performed_by"]

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return f"{obj.performed_by.first_name} {obj.performed_by.last_name}".strip()
        return None

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate(self, data):
        material = data.get("material")
        movement_type = data.get("movement_type")
        quantity = data.get("quantity", 0)

        # check sufficient stock for out movements
        if movement_type in ["out", "transfer"] and material:
            if material.current_stock < quantity:
                raise serializers.ValidationError(
                    {
                        "quantity": f"Insufficient stock. Available: {material.current_stock} {material.unit}"
                    }
                )
        return data


class MaterialRequestSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source="material.name")
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    requested_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MaterialRequest
        fields = [
            "id",
            "vessel",
            "vessel_name",
            "material",
            "material_name",
            "requested_by",
            "requested_by_name",
            "approved_by",
            "quantity_needed",
            "status",
            "needed_by",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["requested_by", "approved_by"]

    def get_requested_by_name(self, obj):
        if obj.requested_by:
            return f"{obj.requested_by.first_name} {obj.requested_by.last_name}".strip()
        return None

    def validate_quantity_needed(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value
