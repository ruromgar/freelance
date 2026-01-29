from django.db import models


class QuarterNumber(models.IntegerChoices):
    Q1 = 1, "1T (ene-mar)"
    Q2 = 2, "2T (abr-jun)"
    Q3 = 3, "3T (jul-sep)"
    Q4 = 4, "4T (oct-dic)"


class Quarter(models.Model):
    fiscal_year = models.ForeignKey(
        "FiscalYear",
        on_delete=models.CASCADE,
        related_name="quarters",
        verbose_name="Año fiscal",
    )
    number = models.PositiveSmallIntegerField(
        choices=QuarterNumber.choices,
        verbose_name="Trimestre",
    )
    closed = models.BooleanField(default=False, verbose_name="Cerrado")
    closing_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de cierre"
    )
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Trimestre"
        verbose_name_plural = "Trimestres"
        unique_together = ["fiscal_year", "number"]
        ordering = ["fiscal_year__year", "number"]

    def __str__(self):
        return f"{self.fiscal_year.year} - {self.get_number_display()}"
