from django.urls import path
from . import views

vessel_list = views.VesselViewSet.as_view({"get": "list"})
vessel_create = views.VesselViewSet.as_view({"post": "create"})
vessel_detail = views.VesselViewSet.as_view({"get": "retrieve"})
vessel_update = views.VesselViewSet.as_view({"patch": "partial_update"})
vessel_delete = views.VesselViewSet.as_view({"delete": "destroy"})
vessel_dashboard = views.VesselViewSet.as_view({"get": "dashboard"})
vessel_spec_view = views.VesselViewSet.as_view(
    {"get": "spec", "post": "spec", "put": "spec"}
)
vessel_parts = views.VesselViewSet.as_view({"get": "parts", "post": "parts"})

part_list = views.VesselPartViewSet.as_view({"get": "list"})
part_create = views.VesselPartViewSet.as_view({"post": "create"})
part_detail = views.VesselPartViewSet.as_view({"get": "retrieve"})
part_update = views.VesselPartViewSet.as_view({"patch": "partial_update"})
part_delete = views.VesselPartViewSet.as_view({"delete": "destroy"})

urlpatterns = [
    # vessels
    path("list/", vessel_list, name="vessel-list"),
    path("create/", vessel_create, name="vessel-create"),
    path("dashboard/", vessel_dashboard, name="vessel-dashboard"),
    path("<uuid:pk>/detail/", vessel_detail, name="vessel-detail"),
    path("<uuid:pk>/update/", vessel_update, name="vessel-update"),
    path("<uuid:pk>/delete/", vessel_delete, name="vessel-delete"),
    path("<uuid:pk>/spec/", vessel_spec_view, name="vessel-spec"),
    path("<uuid:pk>/parts/", vessel_parts, name="vessel-parts"),
    # parts
    path("parts/list/", part_list, name="vessel-part-list"),
    path("parts/create/", part_create, name="vessel-part-create"),
    path("parts/<uuid:pk>/detail/", part_detail, name="vessel-part-detail"),
    path("parts/<uuid:pk>/update/", part_update, name="vessel-part-update"),
    path("parts/<uuid:pk>/delete/", part_delete, name="vessel-part-delete"),
]
