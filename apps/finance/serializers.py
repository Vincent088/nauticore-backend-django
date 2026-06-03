from rest_framework import serializers
from django.utils import timezone
from .models import Invoice, InvoiceItem, Payment
from core.validators import validate_no_emoji, validate_no_sql_xss


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "description",
            "quantity",
            "unit",
            "unit_price",
            "total_price",
            "created_at",
        ]
        read_only_fields = ["total_price"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        return value

    def validate_description(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Description must be at least 2 characters."
            )
        return value.strip()


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.ReadOnlyField(source="invoice.invoice_number")
    confirmed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "invoice_number",
            "payment_method",
            "amount",
            "payment_date",
            "reference",
            "status",
            "notes",
            "confirmed_by",
            "confirmed_by_name",
            "receipt_file",
            "created_at",
        ]
        read_only_fields = ["confirmed_by"]

    def get_confirmed_by_name(self, obj):
        if obj.confirmed_by:
            return f"{obj.confirmed_by.first_name} {obj.confirmed_by.last_name}".strip()
        return None

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than 0.")
        return value

    def validate_reference(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.strip()

    def validate_receipt_file(self, value):
        if value:
            max_size = 10 * 1024 * 1024  # 10MB
            if value.size > max_size:
                raise serializers.ValidationError("Receipt file cannot exceed 10MB.")
            allowed_types = [
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/webp",
            ]
            if (
                hasattr(value, "content_type")
                and value.content_type not in allowed_types
            ):
                raise serializers.ValidationError(
                    "Only PDF and image files are allowed for receipts."
                )
        return value


class InvoiceListSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source="contract.client.name")
    vessel_name = serializers.ReadOnlyField(source="contract.vessel.name")
    outstanding_balance = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "client_name",
            "vessel_name",
            "status",
            "currency",
            "total_amount",
            "amount_paid",
            "outstanding_balance",
            "is_overdue",
            "issue_date",
            "due_date",
            "created_at",
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    client_name = serializers.ReadOnlyField(source="contract.client.name")
    vessel_name = serializers.ReadOnlyField(source="contract.vessel.name")
    contract_number = serializers.ReadOnlyField(source="contract.contract_number")
    outstanding_balance = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "contract",
            "contract_number",
            "client_name",
            "vessel_name",
            "status",
            "currency",
            "subtotal",
            "tax_rate",
            "tax_amount",
            "discount",
            "total_amount",
            "amount_paid",
            "outstanding_balance",
            "issue_date",
            "due_date",
            "paid_date",
            "notes",
            "is_overdue",
            "items",
            "payments",
            "created_at",
            "updated_at",
        ]


class InvoiceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "invoice_number",
            "contract",
            "status",
            "currency",
            "tax_rate",
            "discount",
            "issue_date",
            "due_date",
            "notes",
        ]

    def validate_invoice_number(self, value):
        validate_no_emoji(value)
        validate_no_sql_xss(value)
        return value.upper().strip()

    def validate_tax_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Tax rate must be between 0 and 100.")
        return value

    def validate_discount(self, value):
        if value < 0:
            raise serializers.ValidationError("Discount cannot be negative.")
        return value

    def validate(self, data):
        issue_date = data.get("issue_date")
        due_date = data.get("due_date")
        if issue_date and due_date and due_date < issue_date:
            raise serializers.ValidationError(
                {"due_date": "Due date cannot be before issue date."}
            )
        return data
