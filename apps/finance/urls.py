from django.urls import path
from . import views

invoice_list = views.InvoiceViewSet.as_view({"get": "list"})
invoice_create = views.InvoiceViewSet.as_view({"post": "create"})
invoice_detail = views.InvoiceViewSet.as_view({"get": "retrieve"})
invoice_update = views.InvoiceViewSet.as_view({"patch": "partial_update"})
invoice_delete = views.InvoiceViewSet.as_view({"delete": "destroy"})
invoice_items = views.InvoiceViewSet.as_view({"get": "items", "post": "items"})
invoice_payments = views.InvoiceViewSet.as_view({"get": "payments", "post": "payments"})
invoice_send = views.InvoiceViewSet.as_view({"post": "send"})
invoice_overdue = views.InvoiceViewSet.as_view({"get": "overdue"})
invoice_summary = views.InvoiceViewSet.as_view({"get": "summary"})

item_list = views.InvoiceItemViewSet.as_view({"get": "list"})
item_create = views.InvoiceItemViewSet.as_view({"post": "create"})
item_detail = views.InvoiceItemViewSet.as_view({"get": "retrieve"})
item_update = views.InvoiceItemViewSet.as_view({"patch": "partial_update"})
item_delete = views.InvoiceItemViewSet.as_view({"delete": "destroy"})

payment_list = views.PaymentViewSet.as_view({"get": "list"})
payment_create = views.PaymentViewSet.as_view({"post": "create"})
payment_detail = views.PaymentViewSet.as_view({"get": "retrieve"})
payment_update = views.PaymentViewSet.as_view({"patch": "partial_update"})
payment_delete = views.PaymentViewSet.as_view({"delete": "destroy"})
payment_confirm = views.PaymentViewSet.as_view({"post": "confirm"})
payment_reject = views.PaymentViewSet.as_view({"post": "reject"})

urlpatterns = [
    # invoices
    path("invoices/list/", invoice_list, name="invoice-list"),
    path("invoices/create/", invoice_create, name="invoice-create"),
    path("invoices/overdue/", invoice_overdue, name="invoice-overdue"),
    path("invoices/summary/", invoice_summary, name="invoice-summary"),
    path("invoices/<uuid:pk>/detail/", invoice_detail, name="invoice-detail"),
    path("invoices/<uuid:pk>/update/", invoice_update, name="invoice-update"),
    path("invoices/<uuid:pk>/delete/", invoice_delete, name="invoice-delete"),
    path("invoices/<uuid:pk>/items/", invoice_items, name="invoice-items"),
    path("invoices/<uuid:pk>/payments/", invoice_payments, name="invoice-payments"),
    path("invoices/<uuid:pk>/send/", invoice_send, name="invoice-send"),
    # invoice items
    path("items/list/", item_list, name="invoice-item-list"),
    path("items/create/", item_create, name="invoice-item-create"),
    path("items/<uuid:pk>/detail/", item_detail, name="invoice-item-detail"),
    path("items/<uuid:pk>/update/", item_update, name="invoice-item-update"),
    path("items/<uuid:pk>/delete/", item_delete, name="invoice-item-delete"),
    # payments
    path("payments/list/", payment_list, name="payment-list"),
    path("payments/create/", payment_create, name="payment-create"),
    path("payments/<uuid:pk>/detail/", payment_detail, name="payment-detail"),
    path("payments/<uuid:pk>/update/", payment_update, name="payment-update"),
    path("payments/<uuid:pk>/delete/", payment_delete, name="payment-delete"),
    path("payments/<uuid:pk>/confirm/", payment_confirm, name="payment-confirm"),
    path("payments/<uuid:pk>/reject/", payment_reject, name="payment-reject"),
]
