"""Modelo 390 - Resumen anual de IVA.

Resume la actividad de IVA de todo el año fiscal.
"""

from collections import defaultdict
from decimal import Decimal
from typing import TYPE_CHECKING

from apps.fiscal.services.modelo_303 import calculate_modelo_303

if TYPE_CHECKING:
    from apps.fiscal.models import FiscalYear


def calculate_modelo_390(fiscal_year: "FiscalYear") -> dict:
    """Calcula el modelo 390 (resumen anual IVA).

    Suma de los 4 trimestres.

    Args:
        fiscal_year: Año fiscal a calcular

    Returns:
        dict con:
        - total_output_vat: Decimal - Total IVA devengado anual
        - total_input_vat: Decimal - Total IVA soportado anual
        - result: Decimal - Resultado anual
        - vat_breakdown: list[dict] - Desglose por tipo de IVA
        - quarters_detail: list[dict] - Detalle por trimestre
    """
    total_output_vat = Decimal("0")
    total_input_vat = Decimal("0")
    quarters_detail = []

    # Aggregate by VAT type across all quarters
    taxable_base_by_type: dict[int, Decimal] = defaultdict(Decimal)
    output_vat_by_type: dict[int, Decimal] = defaultdict(Decimal)

    for quarter in fiscal_year.quarters.order_by("number"):
        q_result = calculate_modelo_303(quarter)
        total_output_vat += q_result["total_output_vat"]
        total_input_vat += q_result["total_input_vat"]

        # Aggregate VAT breakdown
        for vat_type, base in q_result["taxable_base_by_type"].items():
            taxable_base_by_type[vat_type] += base
        for vat_type, vat in q_result["output_vat_by_type"].items():
            output_vat_by_type[vat_type] += vat

        quarters_detail.append(
            {
                "quarter": quarter.number,
                "output_vat": q_result["total_output_vat"],
                "input_vat": q_result["total_input_vat"],
                "result": q_result["result"],
            }
        )

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
        "total_output_vat": total_output_vat,
        "total_input_vat": total_input_vat,
        "result": total_output_vat - total_input_vat,
        "vat_breakdown": vat_breakdown,
        "quarters_detail": quarters_detail,
    }
