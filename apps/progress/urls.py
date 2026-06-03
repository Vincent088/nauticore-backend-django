from django.urls import path
from . import views

milestone_list = views.MilestoneViewSet.as_view({"get": "list"})
milestone_create = views.MilestoneViewSet.as_view({"post": "create"})
milestone_detail = views.MilestoneViewSet.as_view({"get": "retrieve"})
milestone_update = views.MilestoneViewSet.as_view({"patch": "partial_update"})
milestone_delete = views.MilestoneViewSet.as_view({"delete": "destroy"})
milestone_tasks = views.MilestoneViewSet.as_view({"get": "tasks", "post": "tasks"})
milestone_overdue = views.MilestoneViewSet.as_view({"get": "overdue"})

task_list = views.TaskViewSet.as_view({"get": "list"})
task_create = views.TaskViewSet.as_view({"post": "create"})
task_detail = views.TaskViewSet.as_view({"get": "retrieve"})
task_update = views.TaskViewSet.as_view({"patch": "partial_update"})
task_delete = views.TaskViewSet.as_view({"delete": "destroy"})
task_complete = views.TaskViewSet.as_view({"post": "complete"})
task_progress = views.TaskViewSet.as_view({"post": "update_progress"})

worklog_list = views.WorkLogViewSet.as_view({"get": "list"})
worklog_create = views.WorkLogViewSet.as_view({"post": "create"})
worklog_detail = views.WorkLogViewSet.as_view({"get": "retrieve"})
worklog_update = views.WorkLogViewSet.as_view({"patch": "partial_update"})
worklog_delete = views.WorkLogViewSet.as_view({"delete": "destroy"})
worklog_mine = views.WorkLogViewSet.as_view({"get": "my_logs"})
worklog_summary = views.WorkLogViewSet.as_view({"get": "summary"})

urlpatterns = [
    # milestones
    path("milestones/list/", milestone_list, name="milestone-list"),
    path("milestones/create/", milestone_create, name="milestone-create"),
    path("milestones/overdue/", milestone_overdue, name="milestone-overdue"),
    path("milestones/<uuid:pk>/detail/", milestone_detail, name="milestone-detail"),
    path("milestones/<uuid:pk>/update/", milestone_update, name="milestone-update"),
    path("milestones/<uuid:pk>/delete/", milestone_delete, name="milestone-delete"),
    path("milestones/<uuid:pk>/tasks/", milestone_tasks, name="milestone-tasks"),
    # tasks
    path("tasks/list/", task_list, name="task-list"),
    path("tasks/create/", task_create, name="task-create"),
    path("tasks/<uuid:pk>/detail/", task_detail, name="task-detail"),
    path("tasks/<uuid:pk>/update/", task_update, name="task-update"),
    path("tasks/<uuid:pk>/delete/", task_delete, name="task-delete"),
    path("tasks/<uuid:pk>/complete/", task_complete, name="task-complete"),
    path(
        "tasks/<uuid:pk>/update-progress/", task_progress, name="task-update-progress"
    ),
    # worklogs
    path("worklogs/list/", worklog_list, name="worklog-list"),
    path("worklogs/create/", worklog_create, name="worklog-create"),
    path("worklogs/my-logs/", worklog_mine, name="worklog-my-logs"),
    path("worklogs/summary/", worklog_summary, name="worklog-summary"),
    path("worklogs/<uuid:pk>/detail/", worklog_detail, name="worklog-detail"),
    path("worklogs/<uuid:pk>/update/", worklog_update, name="worklog-update"),
    path("worklogs/<uuid:pk>/delete/", worklog_delete, name="worklog-delete"),
]
