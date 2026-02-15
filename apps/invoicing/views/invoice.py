from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.invoicing.forms.invoice import InvoiceForm
from apps.invoicing.forms.invoice import InvoiceLineItemFormSet
from apps.invoicing.models.invoice import Invoice
from apps.invoicing.services.numbering import get_next_invoice_number
from apps.invoicing.services.permissions import get_user_businesses
from apps.invoicing.services.permissions import require_business
from apps.invoicing.services.permissions import require_role


@login_required
@require_business
def invoice_list(request):
    invoices = Invoice.objects.filter(business_profile=request.business).select_related(
        "client"
    )
    status_filter = request.GET.get("status", "")
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    q = request.GET.get("q", "").strip()
    if q:
        invoices = invoices.filter(number__icontains=q) | invoices.filter(
            client__name__icontains=q
        )
    return render(
        request,
        "invoicing/invoices/list.html",
        {
            "invoices": invoices,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "invoices",
            "status_filter": status_filter,
            "statuses": Invoice.Status.choices,
            "q": q,
        },
    )


@login_required
@require_role("owner", "editor")
def invoice_create(request):
    business = request.business
    if request.method == "POST":
        form = InvoiceForm(request.POST, business_profile=business)
        formset = InvoiceLineItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.business_profile = business
            invoice.number = get_next_invoice_number(business, invoice.issue_date.year)
            invoice.series = (
                invoice.number.split("-")[0] if "-" in invoice.number else ""
            )
            if not invoice.legal_text and business.legal_text:
                invoice.legal_text = business.legal_text
            invoice.save()
            formset.instance = invoice
            formset.save()
            return redirect("invoicing:invoice_detail", pk=invoice.pk)
    else:
        form = InvoiceForm(business_profile=business)
        if business.legal_text:
            form.initial["legal_text"] = business.legal_text
        formset = InvoiceLineItemFormSet()
    return render(
        request,
        "invoicing/invoices/create.html",
        {
            "form": form,
            "formset": formset,
            "business": business,
            "businesses": get_user_businesses(request.user),
            "active_section": "invoices",
        },
    )


@login_required
@require_role("owner", "editor")
def invoice_edit(request, pk):
    business = request.business
    invoice = get_object_or_404(Invoice, pk=pk, business_profile=business)
    if invoice.status != Invoice.Status.DRAFT:
        raise Http404
    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice, business_profile=business)
        formset = InvoiceLineItemFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("invoicing:invoice_detail", pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice, business_profile=business)
        formset = InvoiceLineItemFormSet(instance=invoice)
    return render(
        request,
        "invoicing/invoices/edit.html",
        {
            "form": form,
            "formset": formset,
            "invoice": invoice,
            "business": business,
            "businesses": get_user_businesses(request.user),
            "active_section": "invoices",
        },
    )


@login_required
@require_business
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related("client").prefetch_related("lines"),
        pk=pk,
        business_profile=request.business,
    )
    return render(
        request,
        "invoicing/invoices/detail.html",
        {
            "invoice": invoice,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "invoices",
        },
    )


@login_required
@require_role("owner", "editor")
def invoice_status(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, business_profile=request.business)
    new_status = request.POST.get("status")
    valid_transitions = {
        Invoice.Status.DRAFT: [Invoice.Status.SENT, Invoice.Status.CANCELLED],
        Invoice.Status.SENT: [Invoice.Status.PAID, Invoice.Status.CANCELLED],
        Invoice.Status.PAID: [],
        Invoice.Status.CANCELLED: [Invoice.Status.DRAFT],
    }
    if new_status in valid_transitions.get(invoice.status, []):
        invoice.status = new_status
        invoice.save(update_fields=["status"])
    return redirect("invoicing:invoice_detail", pk=invoice.pk)
