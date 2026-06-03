from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from apps.accounts.models import CustomUser
from apps.vessels.models import Vessel


class Milestone(BaseModel):

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ON_HOLD = "on_hold", "On Hold"
        CANCELLED = "cancelled", "Cancelled"

    vessel = models.ForeignKey(
        Vessel, on_delete=models.CASCADE, related_name="milestones"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NOT_STARTED
    )
    order = models.PositiveIntegerField(default=0)
    completion_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milestones",
    )

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.name} ({self.vessel.name})"

    def update_completion(self):
        tasks = self.tasks.all()
        if not tasks:
            return
        total = sum(t.completion_pct for t in tasks)
        self.completion_pct = round(total / tasks.count(), 2)
        if self.completion_pct >= 100:
            self.status = "completed"
        elif self.completion_pct > 0:
            self.status = "in_progress"
        self.save()


class Task(BaseModel):

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "In Review"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    milestone = models.ForeignKey(
        Milestone, on_delete=models.CASCADE, related_name="tasks"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.TODO
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    completion_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["milestone", "status"]

    def __str__(self):
        return f"{self.name} ({self.milestone.name})"

    def save(self, *args, **kwargs):
        if self.status == "completed":
            self.completion_pct = 100
        super().save(*args, **kwargs)
        self.milestone.update_completion()


class WorkLog(BaseModel):
    vessel = models.ForeignKey(
        Vessel, on_delete=models.CASCADE, related_name="work_logs"
    )
    task = models.ForeignKey(
        Task, on_delete=models.SET_NULL, null=True, blank=True, related_name="work_logs"
    )
    logged_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="work_logs"
    )
    date = models.DateField()
    hours = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0.1)]
    )
    description = models.TextField()
    issues = models.TextField(blank=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"WorkLog — {self.vessel.name} — {self.date}"
