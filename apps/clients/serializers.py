from rest_framework import serializers
from .models import Client, ClientContact


class ClientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientContact
        fields = [
            "id",
            "name",
            "position",
            "email",
            "phone",
            "is_primary",
            "created_at",
        ]


class ClientListSerializer(serializers.ModelSerializer):
    contact_count = serializers.SerializerMethodField()
    vessel_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "code",
            "industry",
            "country",
            "status",
            "email",
            "phone",
            "contact_count",
            "vessel_count",
            "created_at",
        ]

    def get_contact_count(self, obj):
        return obj.contacts.count()

    def get_vessel_count(self, obj):
        return obj.vessels.count() if hasattr(obj, "vessels") else 0


class ClientDetailSerializer(serializers.ModelSerializer):
    contacts = ClientContactSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "code",
            "industry",
            "country",
            "city",
            "address",
            "email",
            "phone",
            "website",
            "status",
            "notes",
            "contacts",
            "created_at",
            "updated_at",
        ]


class ClientWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "name",
            "code",
            "industry",
            "country",
            "city",
            "address",
            "email",
            "phone",
            "website",
            "status",
            "notes",
        ]
