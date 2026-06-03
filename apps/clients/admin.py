from django.contrib import admin
from .models import Client, ClientContact


class ClientContactInline(admin.TabularInline):
    model = ClientContact
    extra = 0
    fields = ["name", "position", "email", "phone", "is_primary"]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "industry", "country", "status", "created_at"]
    list_filter = ["status", "industry", "country"]
    search_fields = ["name", "code", "email"]
    inlines = [ClientContactInline]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        ("Basic Info", {"fields": ("id", "name", "code", "industry", "status")}),
        ("Location", {"fields": ("country", "city", "address")}),
        ("Contact", {"fields": ("email", "phone", "website")}),
        ("Notes", {"fields": ("notes",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    list_display = ["name", "client", "position", "email", "is_primary"]
    list_filter = ["is_primary"]
    search_fields = ["name", "email", "client__name"]
