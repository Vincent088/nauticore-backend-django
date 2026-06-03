from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Milestone, Task, WorkLog
from .serializers import (
    MilestoneListSerializer,
    MilestoneDetailSerializer,
    MilestoneWriteSerializer,
    TaskSerializer,
    WorkLogSerializer,
)


class MilestoneViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["vessel", "status", "assigned_to"]
    search_fields = ["name", "vessel__name"]
    ordering_fields = ["order", "target_date", "completion_pct"]
    ordering = ["order"]

    def get_queryset(self):
        return Milestone.objects.select_related(
            "vessel", "assigned_to"
        ).prefetch_related("tasks")

    def get_serializer_class(self):
        if self.action == "list":
            return MilestoneListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return MilestoneWriteSerializer
        return MilestoneDetailSerializer

    @action(detail=True, methods=["get", "post"])
    def tasks(self, request, pk=None):
        milestone = self.get_object()

        if request.method == "GET":
            serializer = TaskSerializer(milestone.tasks.all(), many=True)
            return Response(serializer.data)

        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(milestone=milestone)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        today = timezone.now().date()
        overdue = Milestone.objects.filter(target_date__lt=today).exclude(
            status__in=["completed", "cancelled"]
        )
        serializer = MilestoneListSerializer(overdue, many=True)
        return Response({"count": overdue.count(), "results": serializer.data})


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["milestone", "status", "priority", "assigned_to"]
    search_fields = ["name", "milestone__name"]

    def get_queryset(self):
        return Task.objects.select_related("milestone", "assigned_to")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = "completed"
        task.completion_pct = 100
        task.completed_date = timezone.now().date()
        task.save()
        return Response({"message": f'Task "{task.name}" marked as completed.'})

    @action(detail=True, methods=["post"])
    def update_progress(self, request, pk=None):
        task = self.get_object()
        pct = request.data.get("completion_pct")

        if pct is None:
            return Response(
                {"error": "completion_pct is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pct = float(pct)
            if not 0 <= pct <= 100:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "completion_pct must be a number between 0 and 100."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task.completion_pct = pct
        if pct == 100:
            task.status = "completed"
            task.completed_date = timezone.now().date()
        elif pct > 0:
            task.status = "in_progress"
        task.save()
        return Response(
            {"message": "Progress updated.", "completion_pct": task.completion_pct}
        )


class WorkLogViewSet(viewsets.ModelViewSet):
    serializer_class = WorkLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["vessel", "task", "logged_by", "date"]
    ordering_fields = ["date", "hours"]
    ordering = ["-date"]

    def get_queryset(self):
        return WorkLog.objects.select_related("vessel", "task", "logged_by")

    def perform_create(self, serializer):
        serializer.save(logged_by=self.request.user)

    @action(detail=False, methods=["get"])
    def my_logs(self, request):
        logs = WorkLog.objects.filter(logged_by=request.user)
        serializer = WorkLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        vessel_id = request.query_params.get("vessel")
        logs = WorkLog.objects.all()
        if vessel_id:
            logs = logs.filter(vessel=vessel_id)
        total_hours = sum(log.hours for log in logs)
        return Response(
            {
                "total_logs": logs.count(),
                "total_hours": float(total_hours),
            }
        )
