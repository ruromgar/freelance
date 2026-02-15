import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from apps.invoicing.models.invoice import Invoice
from apps.invoicing.models.payment import Payment
from apps.invoicing.services.permissions import require_business


@login_required
@require_business
def export_invoices_csv(request):
    invoices = (
        Invoice.objects.filter(business_profile=request.business)
        .select_related("client")
        .order_by("-issue_date")
    )

    status_filter = request.GET.get("status", "")
    if status_filter:
        invoices = invoices.filter(status=status_filter)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="facturas.csv"'
    response.write("\ufeff")  # BOM for Excel UTF-8

    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Número",
            "Cliente",
            "NIF/CIF Cliente",
            "Fecha emisión",
            "Fecha vencimiento",
            "Estado",
            "Base imponible",
            "IVA",
            "Retención IRPF",
            "Total",
            "Moneda",
        ]
    )

    for inv in invoices:
        writer.writerow(
            [
                inv.number,
                inv.client.name,
                inv.client.tax_id or "",
                inv.issue_date.strftime("%d/%m/%Y"),
                inv.due_date.strftime("%d/%m/%Y") if inv.due_date else "",
                inv.get_status_display(),
                str(inv.subtotal).replace(".", ","),
                str(inv.tax_total).replace(".", ","),
                str(inv.withholding_total).replace(".", ","),
                str(inv.total).replace(".", ","),
                inv.currency,
            ]
        )

    return response


@login_required
@require_business
def export_payments_csv(request):
    payments = (
        Payment.objects.filter(invoice__business_profile=request.business)
        .select_related("invoice", "invoice__client")
        .order_by("-date")
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="pagos.csv"'
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Fecha",
            "Factura",
            "Cliente",
            "Método",
            "Importe",
            "Notas",
        ]
    )

    for p in payments:
        writer.writerow(
            [
                p.date.strftime("%d/%m/%Y"),
                p.invoice.number,
                p.invoice.client.name,
                p.get_method_display(),
                str(p.amount).replace(".", ","),
                p.notes or "",
            ]
        )

    return response


@login_required
@require_business
def export_clients_csv(request):
    from apps.invoicing.models.client import Client

    clients = Client.objects.filter(business_profile=request.business).order_by("name")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="clientes.csv"'
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Nombre",
            "NIF/CIF",
            "Dirección",
            "Ciudad",
            "Código postal",
            "Provincia",
            "Email",
            "Teléfono",
            "Notas",
        ]
    )

    for c in clients:
        writer.writerow(
            [
                c.name,
                c.tax_id or "",
                c.address or "",
                c.city or "",
                c.postal_code or "",
                c.province or "",
                c.email or "",
                c.phone or "",
                c.notes or "",
            ]
        )

    return response
