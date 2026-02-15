from decimal import Decimal

from django.db import models


class QuarterlyResult(models.Model):
    quarter = models.OneToOneField(
        "Quarter",
        on_delete=models.CASCADE,
        related_name="result",
        verbose_name="Trimestre",
    )

    # Modelo 303
    modelo_303_calculated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Modelo 303 calculado",
    )
    modelo_303_submitted = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Modelo 303 presentado",
    )

    # Modelo 130
    modelo_130_calculated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Modelo 130 calculado",
    )
    modelo_130_submitted = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Modelo 130 presentado",
    )

    submission_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de presentación"
    )
    notes = models.TextField(blank=True, verbose_name="Notas")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Resultado trimestral"
        verbose_name_plural = "Resultados trimestrales"

    def __str__(self):
        return f"Resultado {self.quarter}"
