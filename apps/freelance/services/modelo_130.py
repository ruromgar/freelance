"""Modelo 130 - Pago fraccionado IRPF (Estimación directa).

Calcula el pago fraccionado trimestral de IRPF:
- Es ACUMULATIVO: incluye desde T1 hasta el trimestre actual del año
- Rendimiento neto = Ingresos - Gastos deducibles - Gastos difícil justificación
- Gastos difícil justificación (solo estimación simplificada): 5% de ingresos, máx 2000€/año
- Pago = 20% del rendimiento neto acumulado
- Se restan retenciones y pagos de trimestres anteriores
"""

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.freelance.models import Quarter

# Máximo anual de gastos de difícil justificación
MAX_HARD_TO_JUSTIFY_EXPENSES = Decimal("2000")
HARD_TO_JUSTIFY_RATE = Decimal("0.05")  # 5%
IRPF_PAYMENT_RATE = Decimal("0.20")  # 20%


def calculate_modelo_130(quarter: "Quarter") -> dict:
    """Calcula el modelo 130 (pago fraccionado IRPF).

    Es acumulativo: incluye T1..Tn del año.

    Args:
        quarter: Trimestre a calcular

    Returns:
        dict con:
        - accumulated_income: Decimal - Ingresos acumulados T1..Tn
        - accumulated_expenses: Decimal - Gastos deducibles acumulados
        - hard_to_justify_expenses: Decimal - 5% de ingresos (máx 2000€/año, solo simplificada)
        - net_income: Decimal - Rendimiento neto acumulado
        - gross_payment: Decimal - 20% del rendimiento neto
        - accumulated_withholdings: Decimal - Retenciones acumuladas
        - previous_payments: Decimal - Pagos 130 de trimestres anteriores
        - result: Decimal - A ingresar (mínimo 0)
    """
    fiscal_year = quarter.fiscal_year
    is_simplified = fiscal_year.estimation_type == "simplified"

    # Obtener todos los trimestres del año hasta el actual (inclusive)
    quarters = fiscal_year.quarters.filter(number__lte=quarter.number).order_by(
        "number"
    )

    # Acumular ingresos y gastos
    accumulated_income = Decimal("0")
    accumulated_expenses = Decimal("0")
    accumulated_withholdings = Decimal("0")

    for q in quarters:
        for income in q.incomes.all():
            accumulated_income += income.taxable_base
            accumulated_withholdings += income.withholding

        for expense in q.expenses.filter(irpf_deductible=True):
            accumulated_expenses += expense.taxable_base

    # Gastos de difícil justificación (solo estimación simplificada)
    hard_to_justify_expenses = Decimal("0")
    if is_simplified:
        hard_to_justify_expenses = min(
            accumulated_income * HARD_TO_JUSTIFY_RATE,
            MAX_HARD_TO_JUSTIFY_EXPENSES,
        )

    # Rendimiento neto
    net_income = accumulated_income - accumulated_expenses - hard_to_justify_expenses

    # Pago bruto (20% del rendimiento neto)
    gross_payment = max(net_income * IRPF_PAYMENT_RATE, Decimal("0"))

    # Pagos de trimestres anteriores del mismo año
    previous_payments = Decimal("0")
    previous_quarters = fiscal_year.quarters.filter(number__lt=quarter.number)
    for prev_q in previous_quarters:
        if hasattr(prev_q, "result") and prev_q.result.modelo_130_submitted is not None:
            previous_payments += prev_q.result.modelo_130_submitted
        elif hasattr(prev_q, "result"):
            previous_payments += prev_q.result.modelo_130_calculated

    # Resultado final (a ingresar, mínimo 0)
    result = max(
        gross_payment - accumulated_withholdings - previous_payments, Decimal("0")
    )

    return {
        "accumulated_income": accumulated_income,
        "accumulated_expenses": accumulated_expenses,
        "hard_to_justify_expenses": hard_to_justify_expenses,
        "net_income": net_income,
        "gross_payment": gross_payment,
        "accumulated_withholdings": accumulated_withholdings,
        "previous_payments": previous_payments,
        "result": result,
    }
