"""Modelo 303 - Declaración trimestral de IVA.

Calcula el IVA a ingresar o compensar para un trimestre:
- IVA devengado (repercutido): suma del IVA cobrado en facturas emitidas
- IVA soportado deducible: suma del IVA pagado en gastos con deducible_iva=True
- Resultado = IVA devengado - IVA soportado (positivo = a ingresar)
"""

from collections import defaultdict
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.freelance.models import Quarter


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
    # IVA devengado (de ingresos)
    output_vat_by_type: dict[int, Decimal] = defaultdict(Decimal)
    taxable_base_by_type: dict[int, Decimal] = defaultdict(Decimal)

    for income in quarter.incomes.all():
        output_vat_by_type[income.vat_type] += income.output_vat
        taxable_base_by_type[income.vat_type] += income.taxable_base

    total_output_vat = sum(output_vat_by_type.values(), Decimal("0"))

    # IVA soportado deducible (de gastos)
    total_input_vat = Decimal("0")
    for expense in quarter.expenses.filter(vat_deductible=True):
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
