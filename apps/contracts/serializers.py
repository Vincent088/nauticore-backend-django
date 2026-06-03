from rest_framework import serializers
from .models import Contract, ContractTerm, PaymentSchedule
from apps.clients.serializers import ClientListSerializer
from apps.vessels.serializers import VesselListSerializer
from core.validators import validate_no_emoji, validate_no_sql_xss


class ContractTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractTerm
        fields = ["id", "title", "description", "order", "created_at"]

    def validate_title(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value

    def validate_description(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value


class PaymentScheduleSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = PaymentSchedule
        fields = [
            "id",
            "title",
            "amount",
            "due_date",
            "status",
            "description",
            "is_overdue",
            "created_at",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value


class ContractListSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source="client.name")
    vessel_name = serializers.ReadOnlyField(source="vessel.name")
    total_paid = serializers.ReadOnlyField()
    outstanding_balance = serializers.ReadOnlyField()

    class Meta:
        model = Contract
        fields = [
            "id",
            "contract_number",
            "title",
            "client_name",
            "vessel_name",
            "status",
            "currency",
            "total_value",
            "total_paid",
            "outstanding_balance",
            "start_date",
            "end_date",
            "created_at",
        ]


class ContractDetailSerializer(serializers.ModelSerializer):
    client = ClientListSerializer(read_only=True)
    vessel = VesselListSerializer(read_only=True)
    contract_terms = ContractTermSerializer(many=True, read_only=True)
    payment_schedules = PaymentScheduleSerializer(many=True, read_only=True)
    total_paid = serializers.ReadOnlyField()
    outstanding_balance = serializers.ReadOnlyField()

    class Meta:
        model = Contract
        fields = [
            "id",
            "contract_number",
            "title",
            "client",
            "vessel",
            "status",
            "currency",
            "total_value",
            "total_paid",
            "outstanding_balance",
            "signed_date",
            "start_date",
            "end_date",
            "description",
            "terms",
            "notes",
            "contract_terms",
            "payment_schedules",
            "created_at",
            "updated_at",
        ]


class ContractWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            "contract_number",
            "title",
            "client",
            "vessel",
            "status",
            "currency",
            "total_value",
            "signed_date",
            "start_date",
            "end_date",
            "description",
            "terms",
            "notes",
        ]

    def validate_contract_number(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.upper().strip()

    def validate_total_value(self, value):
        if value < 0:
            raise serializers.ValidationError("Contract value cannot be negative.")
        return value

    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be before start date."}
            )
        return data
