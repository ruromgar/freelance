"""Modelo 303 - Declaración trimestral de IVA.

Calcula el IVA a ingresar o compensar para un trimestre:
- IVA devengado (repercutido): suma del IVA cobrado en facturas emitidas
- IVA soportado deducible: suma del IVA pagado en gastos con vat_deductible=True
- Resultado = IVA devengado - IVA soportado (positivo = a ingresar)
"""

from collections import defaultdict
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.fiscal.models import Quarter


def calculate_modelo_303(quarter: "Quarter") -> dict:
    """Calcula el modelo 303 (IVA trimestral).

    Args:
        quarter: Trimestre a calcular

    Returns:
        dict con:
        - output_vat_by_type: {21: Decimal, 10: Decimal, ...} IVA devengado por tipo
        - taxable_base_by_type: {21: Decimal, ...} Base imponible por tipo de IVA
        - total_output_vat: Decimal - Total IVA devengado (repercutido)
        - total_input_vat: Decimal - Total IVA soportado deducible
        - result: Decimal (positivo = a ingresar, negativo = a compensar)
    """
    from apps.fiscal.models import Expense
    from apps.invoicing.models import Invoice

    business_profile = quarter.fiscal_year.business_profile
    start_date, end_date = quarter.get_date_range()

    # IVA devengado (de facturas)
    output_vat_by_type: dict[int, Decimal] = defaultdict(Decimal)
    taxable_base_by_type: dict[int, Decimal] = defaultdict(Decimal)

    # Only count sent or paid invoices (not draft or cancelled)
    invoices = Invoice.objects.filter(
        business_profile=business_profile,
        issue_date__range=(start_date, end_date),
        status__in=[Invoice.Status.SENT, Invoice.Status.PAID],
    ).prefetch_related("lines")

    for invoice in invoices:
        for line in invoice.lines.all():
            # Cast Decimal tax_rate to int for grouping (21.00 -> 21)
            vat_type = int(line.tax_rate)
            output_vat_by_type[vat_type] += line.tax_amount
            taxable_base_by_type[vat_type] += line.subtotal

    total_output_vat = sum(output_vat_by_type.values(), Decimal("0"))

    # IVA soportado deducible (de gastos)
    total_input_vat = Decimal("0")
    expenses = Expense.objects.filter(
        business_profile=business_profile,
        date__range=(start_date, end_date),
        vat_deductible=True,
    )
    for expense in expenses:
        total_input_vat += expense.input_vat

    # Resultado
    result = total_output_vat - total_input_vat

    # Combined breakdown for easy template iteration
    vat_breakdown = []
    for vat_type in sorted(taxable_base_by_type.keys(), reverse=True):
        vat_breakdown.append(
            {
                "type": vat_type,
                "base": taxable_base_by_type[vat_type],
                "vat": output_vat_by_type[vat_type],
            }
        )

    return {
        "output_vat_by_type": dict(output_vat_by_type),
        "taxable_base_by_type": dict(taxable_base_by_type),
        "vat_breakdown": vat_breakdown,
        "total_output_vat": total_output_vat,
        "total_input_vat": total_input_vat,
        "result": result,
    }
