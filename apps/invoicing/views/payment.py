from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.invoicing.forms.payment import PaymentForm
from apps.invoicing.forms.payment import QuickPaymentForm
from apps.invoicing.models.invoice import Invoice
from apps.invoicing.models.payment import Payment
from apps.invoicing.services.payment import check_and_update_invoice_status
from apps.invoicing.services.payment import get_invoice_balance
from apps.invoicing.services.payment import get_invoice_paid_amount
from apps.invoicing.services.permissions import get_user_businesses
from apps.invoicing.services.permissions import require_business
from apps.invoicing.services.permissions import require_role


@login_required
@require_business
def payment_list(request):
    payments = (
        Payment.objects.filter(invoice__business_profile=request.business)
        .select_related("invoice", "invoice__client")
        .order_by("-date")
    )
    return render(
        request,
        "invoicing/payments/list.html",
        {
            "payments": payments,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "payments",
        },
    )


@login_required
@require_role("owner", "editor")
def payment_create(request):
    if request.method == "POST":
        form = PaymentForm(request.POST, business_profile=request.business)
        if form.is_valid():
            payment = form.save()
            check_and_update_invoice_status(payment.invoice)
            return redirect("invoicing:payment_list")
    else:
        form = PaymentForm(business_profile=request.business)
    return render(
        request,
        "invoicing/payments/form.html",
        {
            "form": form,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "payments",
            "title": "Nuevo pago",
        },
    )


@login_required
@require_role("owner", "editor")
def payment_create_for_invoice(request, invoice_pk):
    invoice = get_object_or_404(
        Invoice, pk=invoice_pk, business_profile=request.business
    )
    balance = get_invoice_balance(invoice)
    if request.method == "POST":
        form = QuickPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.save()
            check_and_update_invoice_status(invoice)
            return redirect("invoicing:invoice_detail", pk=invoice.pk)
    else:
        from django.utils import timezone

        form = QuickPaymentForm(
            initial={"amount": balance, "date": timezone.now().date()}
        )
    return render(
        request,
        "invoicing/payments/form_for_invoice.html",
        {
            "form": form,
            "invoice": invoice,
            "balance": balance,
            "paid_amount": get_invoice_paid_amount(invoice),
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "invoices",
        },
    )


@login_required
@require_role("owner", "editor")
def payment_edit(request, pk):
    payment = get_object_or_404(
        Payment, pk=pk, invoice__business_profile=request.business
    )
    old_invoice = payment.invoice
    if request.method == "POST":
        form = PaymentForm(
            request.POST, instance=payment, business_profile=request.business
        )
        if form.is_valid():
            payment = form.save()
            check_and_update_invoice_status(old_invoice)
            if payment.invoice != old_invoice:
                check_and_update_invoice_status(payment.invoice)
            return redirect("invoicing:payment_list")
    else:
        form = PaymentForm(instance=payment, business_profile=request.business)
    return render(
        request,
        "invoicing/payments/form.html",
        {
            "form": form,
            "payment": payment,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "payments",
            "title": f"Editar pago #{payment.pk}",
        },
    )


@login_required
@require_role("owner")
def payment_delete(request, pk):
    payment = get_object_or_404(
        Payment, pk=pk, invoice__business_profile=request.business
    )
    invoice = payment.invoice
    if request.method == "POST":
        payment.delete()
        check_and_update_invoice_status(invoice)
        return redirect("invoicing:payment_list")
    return render(
        request,
        "invoicing/payments/delete.html",
        {
            "payment": payment,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "payments",
        },
    )
