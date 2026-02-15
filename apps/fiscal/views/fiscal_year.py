from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.fiscal.forms import FiscalYearForm
from apps.fiscal.models import FiscalYear
from apps.fiscal.services import calculate_modelo_390
from apps.invoicing.services.permissions import require_business


@login_required
@require_business
def fiscal_year_list(request):
    """List all fiscal years."""
    fiscal_years = FiscalYear.objects.filter(
        business_profile=request.business,
    ).order_by("-year")

    return render(
        request,
        "fiscal/fiscal_year/list.html",
        {
            "active_section": "fiscal_years",
            "business": request.business,
            "fiscal_years": fiscal_years,
        },
    )


@login_required
@require_business
def fiscal_year_create(request):
    """Create a new fiscal year with its 4 quarters."""
    if request.method == "POST":
        form = FiscalYearForm(request.POST)
        if form.is_valid():
            fiscal_year = form.save(commit=False)
            fiscal_year.business_profile = request.business
            fiscal_year.save()
            fiscal_year.create_quarters()
            messages.success(request, f"Año fiscal {fiscal_year.year} creado.")
            return redirect("fiscal:fiscal_year_detail", year=fiscal_year.year)
    else:
        # Default to current year if not already existing
        current_year = date.today().year
        existing = FiscalYear.objects.filter(
            business_profile=request.business,
            year=current_year,
        ).exists()
        initial = {"year": current_year if not existing else current_year + 1}
        form = FiscalYearForm(initial=initial)

    return render(
        request,
        "fiscal/fiscal_year/create.html",
        {
            "active_section": "fiscal_years",
            "business": request.business,
            "form": form,
        },
    )


@login_required
@require_business
def fiscal_year_detail(request, year: int):
    """Yearly summary with modelo 390."""
    fiscal_year = get_object_or_404(
        FiscalYear,
        business_profile=request.business,
        year=year,
    )

    # Calculate modelo 390 (annual VAT summary)
    modelo_390 = calculate_modelo_390(fiscal_year)

    quarters = fiscal_year.quarters.order_by("number")

    return render(
        request,
        "fiscal/fiscal_year/detail.html",
        {
            "active_section": "fiscal_years",
            "business": request.business,
            "fiscal_year": fiscal_year,
            "quarters": quarters,
            "modelo_390": modelo_390,
        },
    )


@login_required
@require_business
def fiscal_year_edit(request, year: int):
    """Edit fiscal year settings."""
    fiscal_year = get_object_or_404(
        FiscalYear,
        business_profile=request.business,
        year=year,
    )

    if request.method == "POST":
        form = FiscalYearForm(request.POST, instance=fiscal_year)
        if form.is_valid():
            form.save()
            messages.success(request, "Año fiscal actualizado.")
            return redirect("fiscal:fiscal_year_detail", year=fiscal_year.year)
    else:
        form = FiscalYearForm(instance=fiscal_year)

    return render(
        request,
        "fiscal/fiscal_year/edit.html",
        {
            "active_section": "fiscal_years",
            "business": request.business,
            "fiscal_year": fiscal_year,
            "form": form,
        },
    )
