from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import MaterialCategory, Material, StockMovement, MaterialRequest
from .serializers import (
    MaterialCategorySerializer,
    MaterialListSerializer,
    MaterialDetailSerializer,
    MaterialWriteSerializer,
    StockMovementSerializer,
    MaterialRequestSerializer,
)


class MaterialCategoryViewSet(viewsets.ModelViewSet):
    queryset = MaterialCategory.objects.all()
    serializer_class = MaterialCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "unit"]
    search_fields = ["name", "code", "supplier"]
    ordering_fields = ["name", "current_stock", "unit_price", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Material.objects.select_related("category")

    def get_serializer_class(self):
        if self.action == "list":
            return MaterialListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return MaterialWriteSerializer
        return MaterialDetailSerializer

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        materials = [m for m in Material.objects.all() if m.is_low_stock]
        serializer = MaterialListSerializer(materials, many=True)
        return Response({"count": len(materials), "results": serializer.data})

    @action(detail=True, methods=["get", "post"])
    def movements(self, request, pk=None):
        material = self.get_object()

        if request.method == "GET":
            movements = material.movements.all()
            serializer = StockMovementSerializer(movements, many=True)
            return Response(serializer.data)

        serializer = StockMovementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(material=material, performed_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        materials = Material.objects.all()
        return Response(
            {
                "total_items": materials.count(),
                "low_stock_items": sum(1 for m in materials if m.is_low_stock),
                "total_stock_value": sum(m.stock_value for m in materials),
            }
        )


class StockMovementViewSet(viewsets.ModelViewSet):
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["material", "vessel", "movement_type"]
    search_fields = ["reference", "material__name"]

    def get_queryset(self):
        return StockMovement.objects.select_related(
            "material", "vessel", "performed_by"
        )

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)


class MaterialRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vessel", "material", "status"]

    def get_queryset(self):
        return MaterialRequest.objects.select_related(
            "vessel", "material", "requested_by", "approved_by"
        )

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        material_request = self.get_object()
        if material_request.status != "pending":
            return Response(
                {"error": "Only pending requests can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        material_request.status = "approved"
        material_request.approved_by = request.user
        material_request.save()
        return Response({"message": "Request approved successfully."})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        material_request = self.get_object()
        if material_request.status != "pending":
            return Response(
                {"error": "Only pending requests can be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        material_request.status = "rejected"
        material_request.save()
        return Response({"message": "Request rejected."})
