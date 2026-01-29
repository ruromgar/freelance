from decimal import Decimal

from django.db import models

from apps.freelance.models.income import VATType


class ExpenseCategory(models.TextChoices):
    SOCIAL_SECURITY = "social_security", "Cuota de autónomos"
    SOFTWARE = "software", "Software y suscripciones"
    SUPPLIES = "supplies", "Material de oficina"
    TELECOM = "telecom", "Telefonía e internet"
    TRAINING = "training", "Formación"
    SERVICES = "services", "Servicios profesionales"
    OTHER = "other", "Otros gastos deducibles"


class Expense(models.Model):
    quarter = models.ForeignKey(
        "Quarter",
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="Trimestre",
    )
    date = models.DateField(verbose_name="Fecha")
    concept = models.CharField(max_length=255, verbose_name="Concepto")
    supplier = models.CharField(max_length=255, blank=True, verbose_name="Proveedor")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Referencia")
    category = models.CharField(
        max_length=20,
        choices=ExpenseCategory.choices,
        default=ExpenseCategory.OTHER,
        verbose_name="Categoría",
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
    input_vat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=Decimal("0"),
        verbose_name="IVA soportado",
    )

    # Deductibility
    irpf_deductible = models.BooleanField(default=True, verbose_name="Deducible IRPF")
    vat_deductible = models.BooleanField(default=True, verbose_name="Deducible IVA")

    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} - {self.concept} ({self.taxable_base}€)"

    def save(self, *args, **kwargs):
        self.input_vat = self.taxable_base * self.vat_type / 100
        super().save(*args, **kwargs)

    @property
    def total(self):
        return self.taxable_base + self.input_vat
