from decimal import Decimal

from django.db import models


class VATType(models.IntegerChoices):
    GENERAL = 21, "21%"
    REDUCED = 10, "10%"
    SUPER_REDUCED = 4, "4%"
    EXEMPT = 0, "Exento"


class Income(models.Model):
    quarter = models.ForeignKey(
        "Quarter",
        on_delete=models.CASCADE,
        related_name="incomes",
        verbose_name="Trimestre",
    )
    date = models.DateField(verbose_name="Fecha")
    concept = models.CharField(max_length=255, verbose_name="Concepto")
    client = models.CharField(max_length=255, blank=True, verbose_name="Cliente")
    reference = models.CharField(
        max_length=100, blank=True, verbose_name="Referencia", help_text="Nº factura"
    )

    # Amounts
    taxable_base = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Base imponible"
    )
    vat_type = models.PositiveSmallIntegerField(
        choices=VATType.choices,
        default=VATType.GENERAL,
        verbose_name="Tipo de IVA",
    )
    output_vat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=Decimal("0"),
        verbose_name="IVA repercutido",
    )

    # Withholding
    withholding_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("15"),
        verbose_name="% Retención",
        help_text="% IRPF retenido (15% normal, 7% inicio actividad)",
    )
    withholding = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=Decimal("0"),
        verbose_name="Retención",
    )

    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} - {self.concept} ({self.taxable_base}€)"

    def save(self, *args, **kwargs):
        self.output_vat = self.taxable_base * self.vat_type / 100
        self.withholding = self.taxable_base * self.withholding_rate / 100
        super().save(*args, **kwargs)

    @property
    def invoice_total(self):
        return self.taxable_base + self.output_vat - self.withholding
