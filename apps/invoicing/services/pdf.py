from django.conf import settings
from django.template.loader import render_to_string

from apps.invoicing.models.business import InvoiceTheme


def get_invoice_theme(invoice):
    theme = InvoiceTheme.objects.filter(
        business_profile=invoice.business_profile, is_default=True
    ).first()
    if not theme:
        theme = InvoiceTheme.objects.filter(
            business_profile=invoice.business_profile
        ).first()
    if not theme:
        theme = InvoiceTheme(
            primary_color="#1e3a5f",
            secondary_color="#f0f4f8",
            font_family="sans-serif",
            layout_variant="classic",
        )
    return theme


def render_invoice_html(invoice, theme=None):
    if theme is None:
        theme = get_invoice_theme(invoice)
    variant = theme.layout_variant or "classic"
    template_name = f"invoicing/pdf/{variant}.html"
    context = {
        "invoice": invoice,
        "business": invoice.business_profile,
        "client": invoice.client,
        "lines": invoice.lines.all(),
        "theme": theme,
    }
    return render_to_string(template_name, context)


def generate_invoice_pdf(invoice):
    import weasyprint

    html_string = render_invoice_html(invoice)
    base_url = str(settings.MEDIA_ROOT)
    pdf_bytes = weasyprint.HTML(string=html_string, base_url=base_url).write_pdf()
    return pdf_bytes
