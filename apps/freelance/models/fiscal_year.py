from django.db import models


class EstimationType(models.TextChoices):
    SIMPLIFIED = "simplified", "Estimación directa simplificada"
    NORMAL = "normal", "Estimación directa normal"


class FiscalYear(models.Model):
    year = models.PositiveSmallIntegerField(unique=True, verbose_name="Año")
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

    def __str__(self):
        return str(self.year)
