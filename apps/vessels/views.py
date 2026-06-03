from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Vessel, VesselSpec, VesselPart
from .serializers import (
    VesselListSerializer,
    VesselDetailSerializer,
    VesselWriteSerializer,
    VesselSpecSerializer,
    VesselPartSerializer,
)


class VesselViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "vessel_type", "ship_type", "client"]
    search_fields = ["name", "project_number", "client__name"]
    ordering_fields = ["name", "created_at", "target_date", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Vessel.objects.select_related(
            "client", "project_manager", "spec"
        ).prefetch_related("parts", "milestones")

    def get_serializer_class(self):
        if self.action == "list":
            return VesselListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return VesselWriteSerializer
        return VesselDetailSerializer

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        vessels = Vessel.objects.all()
        total = vessels.count()
        by_status = {}
        for choice in Vessel.Status.choices:
            by_status[choice[0]] = vessels.filter(status=choice[0]).count()

        overdue = sum(1 for v in vessels if v.is_overdue)

        return Response(
            {
                "total": total,
                "by_status": by_status,
                "overdue": overdue,
                "in_progress": by_status.get("in_progress", 0),
            }
        )

    @action(detail=True, methods=["get", "post", "put"])
    def spec(self, request, pk=None):
        vessel = self.get_object()

        if request.method == "GET":
            try:
                serializer = VesselSpecSerializer(vessel.spec)
                return Response(serializer.data)
            except VesselSpec.DoesNotExist:
                return Response({"detail": "No spec found."}, status=404)

        # POST or PUT — create or update spec
        try:
            instance = vessel.spec
            serializer = VesselSpecSerializer(instance, data=request.data, partial=True)
        except VesselSpec.DoesNotExist:
            serializer = VesselSpecSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(vessel=vessel)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def parts(self, request, pk=None):
        vessel = self.get_object()

        if request.method == "GET":
            parts = vessel.parts.all()
            serializer = VesselPartSerializer(parts, many=True)
            return Response(serializer.data)

        serializer = VesselPartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vessel=vessel)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VesselPartViewSet(viewsets.ModelViewSet):
    serializer_class = VesselPartSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["vessel", "status"]
    search_fields = ["name", "part_number", "supplier"]

    def get_queryset(self):
        return VesselPart.objects.select_related("vessel")
