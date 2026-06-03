from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Contract, ContractTerm, PaymentSchedule
from .serializers import (
    ContractListSerializer,
    ContractDetailSerializer,
    ContractWriteSerializer,
    ContractTermSerializer,
    PaymentScheduleSerializer,
)


class ContractViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "currency", "client", "vessel"]
    search_fields = ["contract_number", "title", "client__name"]
    ordering_fields = ["created_at", "total_value", "end_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Contract.objects.select_related("client", "vessel").prefetch_related(
            "contract_terms", "payment_schedules"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ContractListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ContractWriteSerializer
        return ContractDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get", "post"])
    def terms(self, request, pk=None):
        contract = self.get_object()

        if request.method == "GET":
            serializer = ContractTermSerializer(
                contract.contract_terms.all(), many=True
            )
            return Response(serializer.data)

        serializer = ContractTermSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(contract=contract)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"])
    def payment_schedule(self, request, pk=None):
        contract = self.get_object()

        if request.method == "GET":
            serializer = PaymentScheduleSerializer(
                contract.payment_schedules.all(), many=True
            )
            return Response(serializer.data)

        serializer = PaymentScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(contract=contract)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        contracts = Contract.objects.all()
        return Response(
            {
                "total": contracts.count(),
                "active": contracts.filter(status="active").count(),
                "draft": contracts.filter(status="draft").count(),
                "completed": contracts.filter(status="completed").count(),
                "cancelled": contracts.filter(status="cancelled").count(),
                "total_value": sum(c.total_value for c in contracts),
                "total_paid": sum(c.total_paid for c in contracts),
            }
        )


class PaymentScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["contract", "status"]

    def get_queryset(self):
        return PaymentSchedule.objects.select_related("contract")
