import json
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from apps.invoicing.models.invoice import Invoice
from apps.invoicing.services.permissions import get_active_business
from apps.invoicing.services.permissions import get_user_businesses


def get_monthly_revenue(invoices_qs, months=6):
    """Calculate monthly revenue for the last N months."""
    today = date.today()
    labels = []
    revenue_data = []
    outstanding_data = []

    month_names = [
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic",
    ]

    for i in range(months - 1, -1, -1):
        target = today - relativedelta(months=i)
        labels.append(f"{month_names[target.month - 1]} {target.year}")

        month_invoices = invoices_qs.filter(
            issue_date__year=target.year,
            issue_date__month=target.month,
        )
        paid = month_invoices.filter(status=Invoice.Status.PAID)
        sent = month_invoices.filter(status=Invoice.Status.SENT)

        revenue_data.append(float(sum(inv.total for inv in paid)))
        outstanding_data.append(float(sum(inv.total for inv in sent)))

    return labels, revenue_data, outstanding_data


@login_required
def dashboard(request):
    business = get_active_business(request)
    businesses = get_user_businesses(request.user)
    if not business:
        return render(
            request,
            "invoicing/dashboard.html",
            {"business": None, "businesses": businesses},
        )

    now = timezone.now()
    invoices_qs = Invoice.objects.filter(business_profile=business)

    # Stats: this month
    month_invoices = invoices_qs.filter(
        issue_date__year=now.year, issue_date__month=now.month
    )
    month_count = month_invoices.count()

    # Pending amount (sent invoices)
    sent_invoices = invoices_qs.filter(status=Invoice.Status.SENT)
    pending_amount = sum(inv.total for inv in sent_invoices)

    # Paid this month
    paid_month = invoices_qs.filter(
        status=Invoice.Status.PAID,
        issue_date__year=now.year,
        issue_date__month=now.month,
    )
    paid_amount = sum(inv.total for inv in paid_month)

    # Recent invoices
    recent = invoices_qs.select_related("client").order_by("-created_at")[:5]

    # Draft count
    draft_count = invoices_qs.filter(status=Invoice.Status.DRAFT).count()

    # Monthly chart data (last 6 months)
    labels, revenue_data, outstanding_data = get_monthly_revenue(invoices_qs, 6)
    chart_data = json.dumps(
        {
            "labels": labels,
            "revenue": revenue_data,
            "outstanding": outstanding_data,
        }
    )

    return render(
        request,
        "invoicing/dashboard.html",
        {
            "business": business,
            "businesses": businesses,
            "active_section": "dashboard",
            "month_count": month_count,
            "pending_amount": pending_amount,
            "paid_amount": paid_amount,
            "draft_count": draft_count,
            "recent_invoices": recent,
            "chart_data": chart_data,
        },
    )
