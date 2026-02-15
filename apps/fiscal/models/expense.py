from decimal import Decimal

from django.db import models


class VATType(models.IntegerChoices):
    GENERAL = 21, "21%"
    REDUCED = 10, "10%"
    SUPER_REDUCED = 4, "4%"
    EXEMPT = 0, "Exento"


class ExpenseCategory(models.TextChoices):
    SOCIAL_SECURITY = "social_security", "Cuota de autónomos"
    SOFTWARE = "software", "Software y suscripciones"
    SUPPLIES = "supplies", "Material de oficina"
    TELECOM = "telecom", "Telefonía e internet"
    TRAINING = "training", "Formación"
    SERVICES = "services", "Servicios profesionales"
    OTHER = "other", "Otros gastos deducibles"


class Expense(models.Model):
    business_profile = models.ForeignKey(
        "invoicing.BusinessProfile",
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="Empresa",
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

    def get_quarter(self):
        """Return the quarter this expense belongs to, if it exists."""
        from apps.fiscal.models import Quarter

        month = self.date.month
        if month <= 3:
            quarter_num = 1
        elif month <= 6:
            quarter_num = 2
        elif month <= 9:
            quarter_num = 3
        else:
            quarter_num = 4

        return Quarter.objects.filter(
            fiscal_year__business_profile=self.business_profile,
            fiscal_year__year=self.date.year,
            number=quarter_num,
        ).first()
