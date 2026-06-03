from django.urls import path
from . import views

type_list = views.MaintenanceTypeViewSet.as_view({"get": "list"})
type_create = views.MaintenanceTypeViewSet.as_view({"post": "create"})
type_detail = views.MaintenanceTypeViewSet.as_view({"get": "retrieve"})
type_update = views.MaintenanceTypeViewSet.as_view({"patch": "partial_update"})
type_delete = views.MaintenanceTypeViewSet.as_view({"delete": "destroy"})

schedule_list = views.MaintenanceScheduleViewSet.as_view({"get": "list"})
schedule_create = views.MaintenanceScheduleViewSet.as_view({"post": "create"})
schedule_detail = views.MaintenanceScheduleViewSet.as_view({"get": "retrieve"})
schedule_update = views.MaintenanceScheduleViewSet.as_view({"patch": "partial_update"})
schedule_delete = views.MaintenanceScheduleViewSet.as_view({"delete": "destroy"})
schedule_overdue = views.MaintenanceScheduleViewSet.as_view({"get": "overdue"})
schedule_upcoming = views.MaintenanceScheduleViewSet.as_view({"get": "upcoming"})
schedule_dashboard = views.MaintenanceScheduleViewSet.as_view({"get": "dashboard"})
schedule_complete = views.MaintenanceScheduleViewSet.as_view({"post": "complete"})
schedule_parts = views.MaintenanceScheduleViewSet.as_view(
    {"get": "parts", "post": "parts"}
)

history_list = views.ServiceHistoryViewSet.as_view({"get": "list"})
history_create = views.ServiceHistoryViewSet.as_view({"post": "create"})
history_detail = views.ServiceHistoryViewSet.as_view({"get": "retrieve"})
history_update = views.ServiceHistoryViewSet.as_view({"patch": "partial_update"})
history_delete = views.ServiceHistoryViewSet.as_view({"delete": "destroy"})

urlpatterns = [
    # maintenance types
    path("types/list/", type_list, name="maintenance-type-list"),
    path("types/create/", type_create, name="maintenance-type-create"),
    path("types/<uuid:pk>/detail/", type_detail, name="maintenance-type-detail"),
    path("types/<uuid:pk>/update/", type_update, name="maintenance-type-update"),
    path("types/<uuid:pk>/delete/", type_delete, name="maintenance-type-delete"),
    # schedules
    path("schedules/list/", schedule_list, name="maintenance-list"),
    path("schedules/create/", schedule_create, name="maintenance-create"),
    path("schedules/overdue/", schedule_overdue, name="maintenance-overdue"),
    path("schedules/upcoming/", schedule_upcoming, name="maintenance-upcoming"),
    path("schedules/dashboard/", schedule_dashboard, name="maintenance-dashboard"),
    path("schedules/<uuid:pk>/detail/", schedule_detail, name="maintenance-detail"),
    path("schedules/<uuid:pk>/update/", schedule_update, name="maintenance-update"),
    path("schedules/<uuid:pk>/delete/", schedule_delete, name="maintenance-delete"),
    path(
        "schedules/<uuid:pk>/complete/", schedule_complete, name="maintenance-complete"
    ),
    path("schedules/<uuid:pk>/parts/", schedule_parts, name="maintenance-parts"),
    # service history
    path("history/list/", history_list, name="service-history-list"),
    path("history/create/", history_create, name="service-history-create"),
    path("history/<uuid:pk>/detail/", history_detail, name="service-history-detail"),
    path("history/<uuid:pk>/update/", history_update, name="service-history-update"),
    path("history/<uuid:pk>/delete/", history_delete, name="service-history-delete"),
]
