from django.contrib import admin
from django.utils.html import format_html
from .models import MaterialCategory, Material, StockMovement, MaterialRequest


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "color_badge", "material_count", "created_at"]
    search_fields = ["name"]

    def color_badge(self, obj):
        return format_html(
            '<span style="background:{};color:white;padding:3px 12px;'
            'border-radius:4px">{}</span>',
            obj.color,
            obj.color,
        )

    color_badge.short_description = "Color"

    def material_count(self, obj):
        return obj.materials.count()

    material_count.short_description = "Materials"


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "category",
        "unit",
        "current_stock",
        "minimum_stock",
        "low_stock_badge",
        "unit_price",
        "supplier",
    ]
    list_filter = ["category", "unit"]
    search_fields = ["name", "code", "supplier"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def low_stock_badge(self, obj):
        if obj.is_low_stock:
            return format_html(
                '<span style="background:#dc3545;color:white;'
                'padding:3px 8px;border-radius:4px;font-size:11px">LOW</span>'
            )
        return format_html(
            '<span style="background:#198754;color:white;'
            'padding:3px 8px;border-radius:4px;font-size:11px">OK</span>'
        )

    low_stock_badge.short_description = "Stock Status"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        "material",
        "movement_type",
        "quantity",
        "vessel",
        "reference",
        "performed_by",
        "movement_date",
    ]
    list_filter = ["movement_type", "movement_date"]
    search_fields = ["material__name", "reference"]
    readonly_fields = ["id", "created_at"]


@admin.register(MaterialRequest)
class MaterialRequestAdmin(admin.ModelAdmin):
    list_display = [
        "material",
        "vessel",
        "quantity_needed",
        "status",
        "requested_by",
        "needed_by",
    ]
    list_filter = ["status"]
    search_fields = ["material__name", "vessel__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
