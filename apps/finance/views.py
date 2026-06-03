from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum
from .models import Invoice, InvoiceItem, Payment
from .serializers import (
    InvoiceListSerializer,
    InvoiceDetailSerializer,
    InvoiceWriteSerializer,
    InvoiceItemSerializer,
    PaymentSerializer,
)


class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "currency", "contract"]
    search_fields = ["invoice_number", "contract__client__name"]
    ordering_fields = ["created_at", "due_date", "total_amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Invoice.objects.select_related(
            "contract__client",
            "contract__vessel",
        ).prefetch_related("items", "payments")

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return InvoiceWriteSerializer
        return InvoiceDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get", "post"])
    def items(self, request, pk=None):
        invoice = self.get_object()

        if request.method == "GET":
            serializer = InvoiceItemSerializer(invoice.items.all(), many=True)
            return Response(serializer.data)

        serializer = InvoiceItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(invoice=invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"])
    def payments(self, request, pk=None):
        invoice = self.get_object()

        if request.method == "GET":
            serializer = PaymentSerializer(invoice.payments.all(), many=True)
            return Response(serializer.data)

        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # validate payment amount does not exceed outstanding
        amount = serializer.validated_data["amount"]
        if amount > invoice.outstanding_balance:
            return Response(
                {
                    "error": f"Payment amount exceeds outstanding balance of {invoice.outstanding_balance}."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(invoice=invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        invoice = self.get_object()
        if invoice.status != "draft":
            return Response(
                {"error": "Only draft invoices can be sent."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.status = "sent"
        invoice.issue_date = timezone.now().date()
        invoice.save()
        return Response(
            {"message": f"Invoice {invoice.invoice_number} marked as sent."}
        )

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        today = timezone.now().date()
        overdue = Invoice.objects.filter(due_date__lt=today).exclude(
            status__in=["paid", "cancelled"]
        )
        serializer = InvoiceListSerializer(overdue, many=True)
        return Response({"count": overdue.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def summary(self, request):
        invoices = Invoice.objects.all()
        return Response(
            {
                "total_invoices": invoices.count(),
                "draft": invoices.filter(status="draft").count(),
                "sent": invoices.filter(status="sent").count(),
                "partially_paid": invoices.filter(status="partially_paid").count(),
                "paid": invoices.filter(status="paid").count(),
                "overdue": invoices.filter(status="overdue").count(),
                "cancelled": invoices.filter(status="cancelled").count(),
                "total_revenue": float(
                    invoices.filter(status="paid").aggregate(Sum("total_amount"))[
                        "total_amount__sum"
                    ]
                    or 0
                ),
                "total_outstanding": float(
                    sum(
                        i.outstanding_balance
                        for i in invoices.exclude(status__in=["paid", "cancelled"])
                    )
                ),
            }
        )


class InvoiceItemViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["invoice"]

    def get_queryset(self):
        return InvoiceItem.objects.select_related("invoice")


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["invoice", "status", "payment_method"]
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        return Payment.objects.select_related(
            "invoice__contract__client", "confirmed_by"
        )

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        payment = self.get_object()
        if payment.status != "pending":
            return Response(
                {"error": "Only pending payments can be confirmed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment.status = "confirmed"
        payment.confirmed_by = request.user
        payment.save()
        return Response({"message": "Payment confirmed successfully."})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        payment = self.get_object()
        if payment.status != "pending":
            return Response(
                {"error": "Only pending payments can be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment.status = "rejected"
        payment.save()
        return Response({"message": "Payment rejected."})
