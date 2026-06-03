from django.urls import path
from . import views

client_list = views.ClientViewSet.as_view({"get": "list"})
client_create = views.ClientViewSet.as_view({"post": "create"})
client_detail = views.ClientViewSet.as_view({"get": "retrieve"})
client_update = views.ClientViewSet.as_view({"patch": "partial_update"})
client_delete = views.ClientViewSet.as_view({"delete": "destroy"})
client_contacts = views.ClientViewSet.as_view({"get": "contacts"})
client_add_contact = views.ClientViewSet.as_view({"post": "add_contact"})

contact_list = views.ClientContactViewSet.as_view({"get": "list"})
contact_create = views.ClientContactViewSet.as_view({"post": "create"})
contact_detail = views.ClientContactViewSet.as_view({"get": "retrieve"})
contact_update = views.ClientContactViewSet.as_view({"patch": "partial_update"})
contact_delete = views.ClientContactViewSet.as_view({"delete": "destroy"})

urlpatterns = [
    # clients
    path("list/", client_list, name="client-list"),
    path("create/", client_create, name="client-create"),
    path("<uuid:pk>/detail/", client_detail, name="client-detail"),
    path("<uuid:pk>/update/", client_update, name="client-update"),
    path("<uuid:pk>/delete/", client_delete, name="client-delete"),
    path("<uuid:pk>/contacts/", client_contacts, name="client-contacts"),
    path("<uuid:pk>/add-contact/", client_add_contact, name="client-add-contact"),
    # contacts
    path("contacts/list/", contact_list, name="contact-list"),
    path("contacts/create/", contact_create, name="contact-create"),
    path("contacts/<uuid:pk>/detail/", contact_detail, name="contact-detail"),
    path("contacts/<uuid:pk>/update/", contact_update, name="contact-update"),
    path("contacts/<uuid:pk>/delete/", contact_delete, name="contact-delete"),
]
