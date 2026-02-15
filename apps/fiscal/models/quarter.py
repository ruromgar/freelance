from datetime import date

from django.db import models


class QuarterNumber(models.IntegerChoices):
    Q1 = 1, "1T (ene-mar)"
    Q2 = 2, "2T (abr-jun)"
    Q3 = 3, "3T (jul-sep)"
    Q4 = 4, "4T (oct-dic)"


# Quarter date ranges (month, day) for start and end
QUARTER_DATE_RANGES = {
    1: ((1, 1), (3, 31)),
    2: ((4, 1), (6, 30)),
    3: ((7, 1), (9, 30)),
    4: ((10, 1), (12, 31)),
}


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

    def get_date_range(self) -> tuple[date, date]:
        """Return (start_date, end_date) for this quarter."""
        year = self.fiscal_year.year
        start_month, start_day = QUARTER_DATE_RANGES[self.number][0]
        end_month, end_day = QUARTER_DATE_RANGES[self.number][1]
        return (
            date(year, start_month, start_day),
            date(year, end_month, end_day),
        )
