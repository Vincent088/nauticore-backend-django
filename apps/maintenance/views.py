from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import (
    MaintenanceType,
    MaintenanceSchedule,
    MaintenancePart,
    ServiceHistory,
)
from .serializers import (
    MaintenanceTypeSerializer,
    MaintenanceScheduleListSerializer,
    MaintenanceScheduleDetailSerializer,
    MaintenanceScheduleWriteSerializer,
    MaintenancePartSerializer,
    ServiceHistorySerializer,
)


class MaintenanceTypeViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceType.objects.all()
    serializer_class = MaintenanceTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class MaintenanceScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "vessel",
        "status",
        "priority",
        "maintenance_type",
        "assigned_to",
    ]
    search_fields = ["title", "vessel__name", "vessel__project_number"]
    ordering_fields = ["scheduled_date", "priority", "created_at"]
    ordering = ["scheduled_date"]

    def get_queryset(self):
        return MaintenanceSchedule.objects.select_related(
            "vessel", "maintenance_type", "assigned_to"
        ).prefetch_related("parts_used")

    def get_serializer_class(self):
        if self.action == "list":
            return MaintenanceScheduleListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return MaintenanceScheduleWriteSerializer
        return MaintenanceScheduleDetailSerializer

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        today = timezone.now().date()
        overdue = MaintenanceSchedule.objects.filter(
            scheduled_date__lt=today, status="scheduled"
        )
        serializer = MaintenanceScheduleListSerializer(overdue, many=True)
        return Response({"count": overdue.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        today = timezone.now().date()
        in_30 = today + timezone.timedelta(days=30)
        upcoming = MaintenanceSchedule.objects.filter(
            scheduled_date__range=[today, in_30], status="scheduled"
        )
        serializer = MaintenanceScheduleListSerializer(upcoming, many=True)
        return Response({"count": upcoming.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        today = timezone.now().date()
        in_30 = today + timezone.timedelta(days=30)
        schedules = MaintenanceSchedule.objects.all()
        return Response(
            {
                "total": schedules.count(),
                "scheduled": schedules.filter(status="scheduled").count(),
                "in_progress": schedules.filter(status="in_progress").count(),
                "completed": schedules.filter(status="completed").count(),
                "overdue": schedules.filter(
                    scheduled_date__lt=today, status="scheduled"
                ).count(),
                "upcoming_30": schedules.filter(
                    scheduled_date__range=[today, in_30], status="scheduled"
                ).count(),
                "critical": schedules.filter(
                    priority="critical", status="scheduled"
                ).count(),
            }
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        schedule = self.get_object()
        if schedule.status == "completed":
            return Response(
                {"error": "This maintenance is already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        schedule.status = "completed"
        schedule.completed_date = timezone.now().date()
        actual_hours = request.data.get("actual_hours")
        findings = request.data.get("findings", "")
        if actual_hours:
            schedule.actual_hours = actual_hours
        if findings:
            schedule.findings = findings

        # auto-calculate next due date
        if schedule.maintenance_type:
            from datetime import timedelta

            schedule.next_due_date = timezone.now().date() + timedelta(
                days=schedule.maintenance_type.interval_days
            )
        schedule.save()

        # auto-create service history record
        ServiceHistory.objects.create(
            vessel=schedule.vessel,
            maintenance=schedule,
            title=f"Completed: {schedule.title}",
            description=schedule.description,
            service_date=schedule.completed_date,
            performed_by=request.user,
            hours_spent=schedule.actual_hours or 0,
            findings=schedule.findings,
            next_service_date=schedule.next_due_date,
        )

        return Response(
            {
                "message": "Maintenance completed successfully.",
                "next_due_date": schedule.next_due_date,
            }
        )

    @action(detail=True, methods=["get", "post"])
    def parts(self, request, pk=None):
        schedule = self.get_object()

        if request.method == "GET":
            serializer = MaintenancePartSerializer(schedule.parts_used.all(), many=True)
            return Response(serializer.data)

        serializer = MaintenancePartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(maintenance=schedule)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ServiceHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["vessel", "performed_by"]
    search_fields = ["title", "vessel__name"]
    ordering_fields = ["service_date", "created_at"]
    ordering = ["-service_date"]

    def get_queryset(self):
        return ServiceHistory.objects.select_related(
            "vessel", "maintenance", "performed_by"
        )

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)
