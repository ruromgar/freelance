from apps.invoicing.models.invoice import Invoice


def get_invoice_paid_amount(invoice):
    return sum(p.amount for p in invoice.payments.all())


def get_invoice_balance(invoice):
    return invoice.total - get_invoice_paid_amount(invoice)


def check_and_update_invoice_status(invoice):
    if invoice.status == Invoice.Status.CANCELLED:
        return
    paid = get_invoice_paid_amount(invoice)
    if paid >= invoice.total:
        if invoice.status != Invoice.Status.PAID:
            invoice.status = Invoice.Status.PAID
            invoice.save(update_fields=["status"])
    elif invoice.status == Invoice.Status.PAID:
        invoice.status = Invoice.Status.SENT
        invoice.save(update_fields=["status"])
