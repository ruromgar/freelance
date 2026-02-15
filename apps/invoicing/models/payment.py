from django.db import models


class Payment(models.Model):
    class Method(models.TextChoices):
        TRANSFER = "transfer", "Transferencia"
        CASH = "cash", "Efectivo"
        CARD = "card", "Tarjeta"
        OTHER = "other", "Otro"

    invoice = models.ForeignKey(
        "invoicing.Invoice",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Factura",
    )
    amount = models.DecimalField("Importe", max_digits=10, decimal_places=2)
    date = models.DateField("Fecha")
    method = models.CharField(
        "Método de pago",
        max_length=10,
        choices=Method.choices,
        default=Method.TRANSFER,
    )
    notes = models.TextField("Notas", blank=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.amount} € – {self.invoice.number}"
