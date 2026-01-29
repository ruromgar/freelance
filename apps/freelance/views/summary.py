from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

from apps.freelance.models import FiscalYear
from apps.freelance.models import Quarter
from apps.freelance.services import calculate_modelo_130
from apps.freelance.services import calculate_modelo_303
from apps.freelance.services import calculate_modelo_390


def index(request):
    """Dashboard showing all fiscal years or empty state."""
    current_year = timezone.now().year
    fiscal_years = FiscalYear.objects.all()

    context = {
        "fiscal_years": fiscal_years,
        "current_year": current_year,
        "suggested_year": current_year
        if not fiscal_years.filter(year=current_year).exists()
        else None,
    }
    return render(request, "freelance/index.html", context)


def quarterly_summary(request, year: int, quarter: int):
    """Vista de resumen trimestral con cálculos 303 y 130."""
    fiscal_year = get_object_or_404(FiscalYear, year=year)
    quarter_obj = get_object_or_404(Quarter, fiscal_year=fiscal_year, number=quarter)

    # Calcular modelos
    result_303 = calculate_modelo_303(quarter_obj)
    result_130 = calculate_modelo_130(quarter_obj)

    # Obtener resultado guardado si existe
    saved_result = getattr(quarter_obj, "result", None)

    context = {
        "fiscal_year": fiscal_year,
        "quarter": quarter_obj,
        "incomes": quarter_obj.incomes.all(),
        "expenses": quarter_obj.expenses.all(),
        "result_303": result_303,
        "result_130": result_130,
        "saved_result": saved_result,
    }

    return render(request, "freelance/quarterly_summary.html", context)


def yearly_summary(request, year: int):
    """Vista de resumen anual con cálculo 390."""
    from django.db.models import Sum

    fiscal_year = get_object_or_404(FiscalYear, year=year)

    # Calcular modelo 390
    result_390 = calculate_modelo_390(fiscal_year)

    # Obtener resumen de cada trimestre
    quarters_summary = []
    for quarter in fiscal_year.quarters.order_by("number"):
        result_303 = calculate_modelo_303(quarter)
        result_130 = calculate_modelo_130(quarter)
        saved_result = getattr(quarter, "result", None)

        # Per-quarter totals (not cumulative)
        quarter_income = quarter.incomes.aggregate(total=Sum("taxable_base"))["total"]
        quarter_expenses = quarter.expenses.aggregate(total=Sum("taxable_base"))[
            "total"
        ]

        quarters_summary.append(
            {
                "quarter": quarter,
                "result_303": result_303,
                "result_130": result_130,
                "saved_result": saved_result,
                "total_income": quarter_income,
                "total_expenses": quarter_expenses,
            }
        )

    # Check if year can be closed (all 4 quarters exist and are closed)
    all_quarters = fiscal_year.quarters.all()
    can_close_year = (
        all_quarters.count() == 4 and not all_quarters.filter(closed=False).exists()
    )

    context = {
        "fiscal_year": fiscal_year,
        "quarters_summary": quarters_summary,
        "result_390": result_390,
        "can_close_year": can_close_year,
    }

    return render(request, "freelance/yearly_summary.html", context)


def close_year(request, year: int):
    """Close a fiscal year (requires all 4 quarters closed)."""
    fiscal_year = get_object_or_404(FiscalYear, year=year)

    if fiscal_year.closed:
        messages.warning(request, f"El año {year} ya está cerrado.")
        return redirect("freelance:yearly_summary", year=year)

    quarters = fiscal_year.quarters.all()
    if quarters.count() < 4:
        messages.error(request, f"El año {year} no tiene los 4 trimestres.")
        return redirect("freelance:yearly_summary", year=year)

    if quarters.filter(closed=False).exists():
        messages.error(request, f"El año {year} tiene trimestres sin cerrar.")
        return redirect("freelance:yearly_summary", year=year)

    fiscal_year.closed = True
    fiscal_year.save()
    messages.success(request, f"Año fiscal {year} cerrado correctamente.")
    return redirect("freelance:yearly_summary", year=year)
