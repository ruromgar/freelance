from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.fiscal.models import FiscalYear
from apps.invoicing.services.permissions import require_business


@login_required
@require_business
def fiscal_dashboard(request):
    """Fiscal overview: current year, pending modelos, summary."""
    current_year = date.today().year

    # Get current fiscal year if it exists
    fiscal_year = FiscalYear.objects.filter(
        business_profile=request.business,
        year=current_year,
    ).first()

    # Get all fiscal years for this business
    fiscal_years = FiscalYear.objects.filter(
        business_profile=request.business,
    ).order_by("-year")[:5]

    # Calculate current quarter
    month = date.today().month
    if month <= 3:
        current_quarter_num = 1
    elif month <= 6:
        current_quarter_num = 2
    elif month <= 9:
        current_quarter_num = 3
    else:
        current_quarter_num = 4

    current_quarter = None
    if fiscal_year:
        current_quarter = fiscal_year.quarters.filter(
            number=current_quarter_num
        ).first()

    return render(
        request,
        "fiscal/dashboard.html",
        {
            "active_section": "fiscal_dashboard",
            "business": request.business,
            "fiscal_year": fiscal_year,
            "fiscal_years": fiscal_years,
            "current_quarter": current_quarter,
            "current_quarter_num": current_quarter_num,
        },
    )
