from django.urls import path

from apps.invoicing.views.business import business_create
from apps.invoicing.views.business import business_delete
from apps.invoicing.views.business import business_edit
from apps.invoicing.views.business import business_members
from apps.invoicing.views.business import business_switch
from apps.invoicing.views.catalog import catalog_create
from apps.invoicing.views.catalog import catalog_delete
from apps.invoicing.views.catalog import catalog_edit
from apps.invoicing.views.catalog import catalog_json
from apps.invoicing.views.catalog import catalog_list
from apps.invoicing.views.client import client_create
from apps.invoicing.views.client import client_delete
from apps.invoicing.views.client import client_edit
from apps.invoicing.views.client import client_list
from apps.invoicing.views.dashboard import dashboard
from apps.invoicing.views.export import export_clients_csv
from apps.invoicing.views.export import export_invoices_csv
from apps.invoicing.views.export import export_payments_csv
from apps.invoicing.views.invoice import invoice_create
from apps.invoicing.views.invoice import invoice_detail
from apps.invoicing.views.invoice import invoice_edit
from apps.invoicing.views.invoice import invoice_list
from apps.invoicing.views.invoice import invoice_status
from apps.invoicing.views.numbering import numbering_settings
from apps.invoicing.views.payment import payment_create
from apps.invoicing.views.payment import payment_create_for_invoice
from apps.invoicing.views.payment import payment_delete
from apps.invoicing.views.payment import payment_edit
from apps.invoicing.views.payment import payment_list
from apps.invoicing.views.pdf import invoice_pdf
from apps.invoicing.views.pdf import invoice_preview
from apps.invoicing.views.settings import theme_create
from apps.invoicing.views.settings import theme_delete
from apps.invoicing.views.settings import theme_edit
from apps.invoicing.views.settings import theme_list

app_name = "invoicing"

urlpatterns = [
    # Dashboard
    path("", dashboard, name="dashboard"),
    # Business
    path("empresa/nueva/", business_create, name="business_create"),
    path("empresa/editar/", business_edit, name="business_edit"),
    path("empresa/eliminar/", business_delete, name="business_delete"),
    path("empresa/cambiar/<int:pk>/", business_switch, name="business_switch"),
    path("empresa/usuarios/", business_members, name="business_members"),
    # Clients
    path("clientes/", client_list, name="client_list"),
    path("clientes/nuevo/", client_create, name="client_create"),
    path("clientes/<int:pk>/editar/", client_edit, name="client_edit"),
    path("clientes/<int:pk>/eliminar/", client_delete, name="client_delete"),
    # Catalog
    path("catalogo/", catalog_list, name="catalog_list"),
    path("catalogo/nuevo/", catalog_create, name="catalog_create"),
    path("catalogo/<int:pk>/editar/", catalog_edit, name="catalog_edit"),
    path("catalogo/<int:pk>/eliminar/", catalog_delete, name="catalog_delete"),
    path("catalogo/json/", catalog_json, name="catalog_json"),
    # Invoices
    path("facturas/", invoice_list, name="invoice_list"),
    path("facturas/nueva/", invoice_create, name="invoice_create"),
    path("facturas/<int:pk>/", invoice_detail, name="invoice_detail"),
    path("facturas/<int:pk>/editar/", invoice_edit, name="invoice_edit"),
    path("facturas/<int:pk>/estado/", invoice_status, name="invoice_status"),
    path("facturas/<int:pk>/vista-previa/", invoice_preview, name="invoice_preview"),
    path("facturas/<int:pk>/pdf/", invoice_pdf, name="invoice_pdf"),
    path(
        "facturas/<int:invoice_pk>/pago/",
        payment_create_for_invoice,
        name="payment_create_for_invoice",
    ),
    # Payments
    path("pagos/", payment_list, name="payment_list"),
    path("pagos/nuevo/", payment_create, name="payment_create"),
    path("pagos/<int:pk>/editar/", payment_edit, name="payment_edit"),
    path("pagos/<int:pk>/eliminar/", payment_delete, name="payment_delete"),
    # Settings - Themes
    path("ajustes/temas/", theme_list, name="theme_list"),
    path("ajustes/temas/nuevo/", theme_create, name="theme_create"),
    path("ajustes/temas/<int:pk>/editar/", theme_edit, name="theme_edit"),
    path("ajustes/temas/<int:pk>/eliminar/", theme_delete, name="theme_delete"),
    # Settings - Numbering
    path("ajustes/numeracion/", numbering_settings, name="numbering_settings"),
    # Exports
    path("exportar/facturas/", export_invoices_csv, name="export_invoices_csv"),
    path("exportar/pagos/", export_payments_csv, name="export_payments_csv"),
    path("exportar/clientes/", export_clients_csv, name="export_clients_csv"),
]
