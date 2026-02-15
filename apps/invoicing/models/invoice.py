from decimal import Decimal

from django.db import models


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        SENT = "sent", "Enviada"
        PAID = "paid", "Pagada"
        CANCELLED = "cancelled", "Anulada"

    business_profile = models.ForeignKey(
        "invoicing.BusinessProfile",
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name="Empresa",
    )
    client = models.ForeignKey(
        "invoicing.Client",
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name="Cliente",
    )
    number = models.CharField("Número", max_length=50)
    series = models.CharField("Serie", max_length=10, blank=True)
    status = models.CharField(
        "Estado",
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    currency = models.CharField("Moneda", max_length=3, default="EUR")
    issue_date = models.DateField("Fecha de emisión")
    due_date = models.DateField("Fecha de vencimiento", blank=True, null=True)
    notes = models.TextField("Notas", blank=True)
    legal_text = models.TextField("Texto legal", blank=True)
    pdf_file = models.FileField("PDF", upload_to="invoices/", blank=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha de actualización", auto_now=True)

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ["-issue_date", "-number"]
        unique_together = ("business_profile", "number")

    def __str__(self):
        return f"{self.number} – {self.client}"

    @property
    def subtotal(self):
        return sum(line.subtotal for line in self.lines.all())

    @property
    def tax_total(self):
        return sum(line.tax_amount for line in self.lines.all())

    @property
    def withholding_total(self):
        return sum(line.withholding_amount for line in self.lines.all())

    @property
    def total(self):
        return self.subtotal + self.tax_total - self.withholding_total


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Factura",
    )
    description = models.CharField("Descripción", max_length=500)
    quantity = models.DecimalField(
        "Cantidad", max_digits=10, decimal_places=2, default=1
    )
    unit_price = models.DecimalField("Precio unitario", max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(
        "IVA (%)", max_digits=5, decimal_places=2, default=21
    )
    withholding_rate = models.DecimalField(
        "Retención IRPF (%)", max_digits=5, decimal_places=2, default=0
    )
    discount_percent = models.DecimalField(
        "Descuento (%)", max_digits=5, decimal_places=2, default=0
    )
    position = models.PositiveIntegerField("Posición", default=0)

    class Meta:
        verbose_name = "Línea de factura"
        verbose_name_plural = "Líneas de factura"
        ordering = ["position"]

    def __str__(self):
        return self.description

    @property
    def subtotal(self):
        return (
            self.quantity
            * self.unit_price
            * (Decimal("1") - self.discount_percent / Decimal("100"))
        )

    @property
    def tax_amount(self):
        return self.subtotal * self.tax_rate / Decimal("100")

    @property
    def withholding_amount(self):
        return self.subtotal * self.withholding_rate / Decimal("100")

    @property
    def line_total(self):
        return self.subtotal + self.tax_amount - self.withholding_amount
