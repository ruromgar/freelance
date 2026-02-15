from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from apps.fiscal.forms import QuarterlyResultForm
from apps.fiscal.models import FiscalYear
from apps.fiscal.models import Quarter
from apps.fiscal.models import QuarterlyResult
from apps.fiscal.services import calculate_modelo_130
from apps.fiscal.services import calculate_modelo_303
from apps.invoicing.services.permissions import require_business


@login_required
@require_business
def quarter_detail(request, year: int, quarter_num: int):
    """Quarterly summary with modelos 303 and 130."""
    fiscal_year = get_object_or_404(
        FiscalYear,
        business_profile=request.business,
        year=year,
    )

    quarter = get_object_or_404(
        Quarter,
        fiscal_year=fiscal_year,
        number=quarter_num,
    )

    # Calculate modelos
    modelo_303 = calculate_modelo_303(quarter)
    modelo_130 = calculate_modelo_130(quarter)

    # Get or create result for form
    result, _ = QuarterlyResult.objects.get_or_create(quarter=quarter)

    return render(
        request,
        "fiscal/quarter/detail.html",
        {
            "active_section": "fiscal_years",
            "business": request.business,
            "fiscal_year": fiscal_year,
            "quarter": quarter,
            "modelo_303": modelo_303,
            "modelo_130": modelo_130,
            "result": result,
        },
    )


@login_required
@require_business
def quarter_save_result(request, year: int, quarter_num: int):
    """Save calculated results and optionally submitted values."""
    fiscal_year = get_object_or_404(
        FiscalYear,
        business_profile=request.business,
        year=year,
    )

    quarter = get_object_or_404(
        Quarter,
        fiscal_year=fiscal_year,
        number=quarter_num,
    )

    # Calculate modelos
    modelo_303 = calculate_modelo_303(quarter)
    modelo_130 = calculate_modelo_130(quarter)

    result, _ = QuarterlyResult.objects.get_or_create(quarter=quarter)

    if request.method == "POST":
        form = QuarterlyResultForm(request.POST, instance=result)
        if form.is_valid():
            result = form.save(commit=False)
            result.modelo_303_calculated = modelo_303["result"]
            result.modelo_130_calculated = modelo_130["result"]
            result.save()
            messages.success(request, "Resultado guardado.")
            return redirect("fiscal:quarter_detail", year=year, quarter_num=quarter_num)
    else:
        form = QuarterlyResultForm(instance=result)

    return render(
        request,
        "fiscal/quarter/save_result.html",
        {
            "active_section": "fiscal_years",
            "business": request.business,
            "fiscal_year": fiscal_year,
            "quarter": quarter,
            "modelo_303": modelo_303,
            "modelo_130": modelo_130,
            "result": result,
            "form": form,
        },
    )


@login_required
@require_business
def quarter_close(request, year: int, quarter_num: int):
    """Close a quarter."""
    fiscal_year = get_object_or_404(
        FiscalYear,
        business_profile=request.business,
        year=year,
    )

    quarter = get_object_or_404(
        Quarter,
        fiscal_year=fiscal_year,
        number=quarter_num,
    )

    if request.method == "POST":
        # Ensure result exists
        if not hasattr(quarter, "result"):
            messages.error(request, "Debes guardar el resultado antes de cerrar.")
            return redirect("fiscal:quarter_detail", year=year, quarter_num=quarter_num)

        quarter.closed = True
        quarter.closing_date = timezone.now().date()
        quarter.save()
        messages.success(request, f"Trimestre {quarter.get_number_display()} cerrado.")
        return redirect("fiscal:fiscal_year_detail", year=year)

    return render(
        request,
        "fiscal/quarter/close_confirm.html",
        {
            "active_section": "fiscal_years",
            "business": request.business,
            "fiscal_year": fiscal_year,
            "quarter": quarter,
        },
    )
