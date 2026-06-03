from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Client, ClientContact
from .serializers import (
    ClientListSerializer,
    ClientDetailSerializer,
    ClientWriteSerializer,
    ClientContactSerializer,
)


class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "industry", "country"]
    search_fields = ["name", "code", "email", "country"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Client.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ClientListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return ClientWriteSerializer
        return ClientDetailSerializer

    @action(detail=True, methods=["get"])
    def contacts(self, request, pk=None):
        client = self.get_object()
        contacts = client.contacts.all()
        serializer = ClientContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_contact(self, request, pk=None):
        client = self.get_object()
        serializer = ClientContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientContactViewSet(viewsets.ModelViewSet):
    serializer_class = ClientContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["client", "is_primary"]
    search_fields = ["name", "email", "position"]

    def get_queryset(self):
        return ClientContact.objects.all()
