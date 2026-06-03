from django.urls import path
from . import views

doc_list = views.DocumentViewSet.as_view({"get": "list"})
doc_create = views.DocumentViewSet.as_view({"post": "create"})
doc_detail = views.DocumentViewSet.as_view({"get": "retrieve"})
doc_update = views.DocumentViewSet.as_view({"patch": "partial_update"})
doc_delete = views.DocumentViewSet.as_view({"delete": "destroy"})
doc_expiring = views.DocumentViewSet.as_view({"get": "expiring"})
doc_expired = views.DocumentViewSet.as_view({"get": "expired"})

cert_list = views.CertificationViewSet.as_view({"get": "list"})
cert_create = views.CertificationViewSet.as_view({"post": "create"})
cert_detail = views.CertificationViewSet.as_view({"get": "retrieve"})
cert_update = views.CertificationViewSet.as_view({"patch": "partial_update"})
cert_delete = views.CertificationViewSet.as_view({"delete": "destroy"})
cert_expiring = views.CertificationViewSet.as_view({"get": "expiring"})
cert_expired = views.CertificationViewSet.as_view({"get": "expired"})
cert_refresh = views.CertificationViewSet.as_view({"post": "refresh_status"})

urlpatterns = [
    # documents
    path("list/", doc_list, name="document-list"),
    path("create/", doc_create, name="document-create"),
    path("expiring/", doc_expiring, name="document-expiring"),
    path("expired/", doc_expired, name="document-expired"),
    path("<uuid:pk>/detail/", doc_detail, name="document-detail"),
    path("<uuid:pk>/update/", doc_update, name="document-update"),
    path("<uuid:pk>/delete/", doc_delete, name="document-delete"),
    # certifications
    path("certifications/list/", cert_list, name="cert-list"),
    path("certifications/create/", cert_create, name="cert-create"),
    path("certifications/expiring/", cert_expiring, name="cert-expiring"),
    path("certifications/expired/", cert_expired, name="cert-expired"),
    path("certifications/<uuid:pk>/detail/", cert_detail, name="cert-detail"),
    path("certifications/<uuid:pk>/update/", cert_update, name="cert-update"),
    path("certifications/<uuid:pk>/delete/", cert_delete, name="cert-delete"),
    path("certifications/<uuid:pk>/refresh-status/", cert_refresh, name="cert-refresh"),
]
