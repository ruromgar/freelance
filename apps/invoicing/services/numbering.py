from apps.invoicing.models.business import InvoiceNumbering


def get_next_invoice_number(business_profile, year):
    numbering, created = InvoiceNumbering.objects.get_or_create(
        business_profile=business_profile,
        defaults={"series_prefix": "F", "next_number": 1},
    )
    return numbering.generate_number(year)
