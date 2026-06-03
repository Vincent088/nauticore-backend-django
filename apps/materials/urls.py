from django.urls import path
from . import views

material_list = views.MaterialViewSet.as_view({"get": "list"})
material_create = views.MaterialViewSet.as_view({"post": "create"})
material_detail = views.MaterialViewSet.as_view({"get": "retrieve"})
material_update = views.MaterialViewSet.as_view({"patch": "partial_update"})
material_delete = views.MaterialViewSet.as_view({"delete": "destroy"})
material_low = views.MaterialViewSet.as_view({"get": "low_stock"})
material_summary = views.MaterialViewSet.as_view({"get": "summary"})
material_movements = views.MaterialViewSet.as_view(
    {"get": "movements", "post": "movements"}
)

category_list = views.MaterialCategoryViewSet.as_view({"get": "list"})
category_create = views.MaterialCategoryViewSet.as_view({"post": "create"})
category_detail = views.MaterialCategoryViewSet.as_view({"get": "retrieve"})
category_update = views.MaterialCategoryViewSet.as_view({"patch": "partial_update"})
category_delete = views.MaterialCategoryViewSet.as_view({"delete": "destroy"})

movement_list = views.StockMovementViewSet.as_view({"get": "list"})
movement_create = views.StockMovementViewSet.as_view({"post": "create"})
movement_detail = views.StockMovementViewSet.as_view({"get": "retrieve"})
movement_delete = views.StockMovementViewSet.as_view({"delete": "destroy"})

request_list = views.MaterialRequestViewSet.as_view({"get": "list"})
request_create = views.MaterialRequestViewSet.as_view({"post": "create"})
request_detail = views.MaterialRequestViewSet.as_view({"get": "retrieve"})
request_update = views.MaterialRequestViewSet.as_view({"patch": "partial_update"})
request_delete = views.MaterialRequestViewSet.as_view({"delete": "destroy"})
request_approve = views.MaterialRequestViewSet.as_view({"post": "approve"})
request_reject = views.MaterialRequestViewSet.as_view({"post": "reject"})

urlpatterns = [
    # materials
    path("list/", material_list, name="material-list"),
    path("create/", material_create, name="material-create"),
    path("low-stock/", material_low, name="material-low-stock"),
    path("summary/", material_summary, name="material-summary"),
    path("<uuid:pk>/detail/", material_detail, name="material-detail"),
    path("<uuid:pk>/update/", material_update, name="material-update"),
    path("<uuid:pk>/delete/", material_delete, name="material-delete"),
    path("<uuid:pk>/movements/", material_movements, name="material-movements"),
    # categories
    path("categories/list/", category_list, name="category-list"),
    path("categories/create/", category_create, name="category-create"),
    path("categories/<uuid:pk>/detail/", category_detail, name="category-detail"),
    path("categories/<uuid:pk>/update/", category_update, name="category-update"),
    path("categories/<uuid:pk>/delete/", category_delete, name="category-delete"),
    # movements
    path("movements/list/", movement_list, name="movement-list"),
    path("movements/create/", movement_create, name="movement-create"),
    path("movements/<uuid:pk>/detail/", movement_detail, name="movement-detail"),
    path("movements/<uuid:pk>/delete/", movement_delete, name="movement-delete"),
    # requests
    path("requests/list/", request_list, name="request-list"),
    path("requests/create/", request_create, name="request-create"),
    path("requests/<uuid:pk>/detail/", request_detail, name="request-detail"),
    path("requests/<uuid:pk>/update/", request_update, name="request-update"),
    path("requests/<uuid:pk>/delete/", request_delete, name="request-delete"),
    path("requests/<uuid:pk>/approve/", request_approve, name="request-approve"),
    path("requests/<uuid:pk>/reject/", request_reject, name="request-reject"),
]
