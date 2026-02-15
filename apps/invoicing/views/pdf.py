from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from apps.invoicing.models.invoice import Invoice
from apps.invoicing.services.pdf import generate_invoice_pdf
from apps.invoicing.services.pdf import get_invoice_theme
from apps.invoicing.services.pdf import render_invoice_html
from apps.invoicing.services.permissions import require_business


@login_required
@require_business
def invoice_preview(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related("client", "business_profile").prefetch_related(
            "lines"
        ),
        pk=pk,
        business_profile=request.business,
    )
    theme = get_invoice_theme(invoice)
    html = render_invoice_html(invoice, theme)
    return render(
        request,
        "invoicing/invoices/preview.html",
        {"invoice": invoice, "preview_html": html},
    )


@login_required
@require_business
def invoice_pdf(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related("client", "business_profile").prefetch_related(
            "lines"
        ),
        pk=pk,
        business_profile=request.business,
    )
    pdf_bytes = generate_invoice_pdf(invoice)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    filename = f"{invoice.number}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
