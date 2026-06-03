from django.urls import path
from . import views

contract_list = views.ContractViewSet.as_view({"get": "list"})
contract_create = views.ContractViewSet.as_view({"post": "create"})
contract_detail = views.ContractViewSet.as_view({"get": "retrieve"})
contract_update = views.ContractViewSet.as_view({"patch": "partial_update"})
contract_delete = views.ContractViewSet.as_view({"delete": "destroy"})
contract_terms = views.ContractViewSet.as_view({"get": "terms", "post": "terms"})
contract_schedule = views.ContractViewSet.as_view(
    {"get": "payment_schedule", "post": "payment_schedule"}
)
contract_summary = views.ContractViewSet.as_view({"get": "summary"})

schedule_list = views.PaymentScheduleViewSet.as_view({"get": "list"})
schedule_create = views.PaymentScheduleViewSet.as_view({"post": "create"})
schedule_detail = views.PaymentScheduleViewSet.as_view({"get": "retrieve"})
schedule_update = views.PaymentScheduleViewSet.as_view({"patch": "partial_update"})
schedule_delete = views.PaymentScheduleViewSet.as_view({"delete": "destroy"})

urlpatterns = [
    # contracts
    path("list/", contract_list, name="contract-list"),
    path("create/", contract_create, name="contract-create"),
    path("summary/", contract_summary, name="contract-summary"),
    path("<uuid:pk>/detail/", contract_detail, name="contract-detail"),
    path("<uuid:pk>/update/", contract_update, name="contract-update"),
    path("<uuid:pk>/delete/", contract_delete, name="contract-delete"),
    path("<uuid:pk>/terms/", contract_terms, name="contract-terms"),
    path(
        "<uuid:pk>/payment-schedule/",
        contract_schedule,
        name="contract-payment-schedule",
    ),
    # payment schedules
    path("schedules/list/", schedule_list, name="schedule-list"),
    path("schedules/create/", schedule_create, name="schedule-create"),
    path("schedules/<uuid:pk>/detail/", schedule_detail, name="schedule-detail"),
    path("schedules/<uuid:pk>/update/", schedule_update, name="schedule-update"),
    path("schedules/<uuid:pk>/delete/", schedule_delete, name="schedule-delete"),
]
