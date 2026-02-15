from django.db import models


class EstimationType(models.TextChoices):
    SIMPLIFIED = "simplified", "Estimación directa simplificada"
    NORMAL = "normal", "Estimación directa normal"


class FiscalYear(models.Model):
    business_profile = models.ForeignKey(
        "invoicing.BusinessProfile",
        on_delete=models.CASCADE,
        related_name="fiscal_years",
        verbose_name="Empresa",
    )
    year = models.PositiveSmallIntegerField(verbose_name="Año")
    estimation_type = models.CharField(
        max_length=20,
        choices=EstimationType.choices,
        default=EstimationType.SIMPLIFIED,
        verbose_name="Tipo de estimación",
    )
    closed = models.BooleanField(default=False, verbose_name="Cerrado")
    notes = models.TextField(blank=True, verbose_name="Notas")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Año fiscal"
        verbose_name_plural = "Años fiscales"
        ordering = ["-year"]
        unique_together = ("business_profile", "year")

    def __str__(self):
        return str(self.year)

    def create_quarters(self):
        """Create the 4 quarters for this fiscal year if they don't exist."""
        from apps.fiscal.models.quarter import Quarter
        from apps.fiscal.models.quarter import QuarterNumber

        for number in QuarterNumber.values:
            Quarter.objects.get_or_create(
                fiscal_year=self,
                number=number,
            )
