from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Document, Certification
from .serializers import DocumentSerializer, CertificationSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["vessel", "document_type", "status"]
    search_fields = ["title", "document_number", "tags"]
    ordering_fields = ["created_at", "title", "expiry_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Document.objects.select_related("vessel", "uploaded_by")

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=False, methods=["get"])
    def expiring(self, request):
        today = timezone.now().date()
        in_30 = today + timezone.timedelta(days=30)
        expiring = Document.objects.filter(expiry_date__range=[today, in_30]).exclude(
            status="archived"
        )
        serializer = DocumentSerializer(expiring, many=True)
        return Response({"count": expiring.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def expired(self, request):
        today = timezone.now().date()
        expired = Document.objects.filter(expiry_date__lt=today).exclude(
            status="archived"
        )
        serializer = DocumentSerializer(expired, many=True)
        return Response({"count": expired.count(), "results": serializer.data})


class CertificationViewSet(viewsets.ModelViewSet):
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["vessel", "cert_type", "status"]
    search_fields = ["title", "cert_number", "issuing_body"]
    ordering_fields = ["expiry_date", "issued_date", "created_at"]
    ordering = ["expiry_date"]

    def get_queryset(self):
        return Certification.objects.select_related("vessel")

    @action(detail=False, methods=["get"])
    def expiring(self, request):
        today = timezone.now().date()
        in_30 = today + timezone.timedelta(days=30)
        expiring = Certification.objects.filter(
            expiry_date__range=[today, in_30]
        ).exclude(status__in=["expired", "revoked"])
        serializer = CertificationSerializer(expiring, many=True)
        return Response({"count": expiring.count(), "results": serializer.data})

    @action(detail=False, methods=["get"])
    def expired(self, request):
        today = timezone.now().date()
        expired = Certification.objects.filter(expiry_date__lt=today).exclude(
            status="revoked"
        )
        serializer = CertificationSerializer(expired, many=True)
        return Response({"count": expired.count(), "results": serializer.data})

    @action(detail=True, methods=["post"])
    def refresh_status(self, request, pk=None):
        cert = self.get_object()
        cert.update_status()
        return Response(
            {
                "message": "Status refreshed.",
                "status": cert.status,
                "days_until_expiry": cert.days_until_expiry,
            }
        )
