from django.db import models


class Client(models.Model):
    business_profile = models.ForeignKey(
        "invoicing.BusinessProfile",
        on_delete=models.CASCADE,
        related_name="clients",
        verbose_name="Empresa",
    )
    name = models.CharField("Nombre", max_length=255)
    tax_id = models.CharField("NIF/CIF", max_length=20, blank=True)
    address = models.CharField("Dirección", max_length=255, blank=True)
    city = models.CharField("Ciudad", max_length=100, blank=True)
    postal_code = models.CharField("Código postal", max_length=10, blank=True)
    province = models.CharField("Provincia", max_length=100, blank=True)
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Teléfono", max_length=20, blank=True)
    notes = models.TextField("Notas", blank=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha de actualización", auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class CatalogItem(models.Model):
    business_profile = models.ForeignKey(
        "invoicing.BusinessProfile",
        on_delete=models.CASCADE,
        related_name="catalog_items",
        verbose_name="Empresa",
    )
    name = models.CharField("Nombre", max_length=255)
    description = models.TextField("Descripción", blank=True)
    default_unit_price = models.DecimalField(
        "Precio unitario", max_digits=10, decimal_places=2, default=0
    )
    default_tax_rate = models.DecimalField(
        "Tipo de IVA (%)", max_digits=5, decimal_places=2, default=21
    )
    default_withholding_rate = models.DecimalField(
        "Retención IRPF (%)", max_digits=5, decimal_places=2, default=0
    )
    active = models.BooleanField("Activo", default=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha de actualización", auto_now=True)

    class Meta:
        verbose_name = "Artículo del catálogo"
        verbose_name_plural = "Artículos del catálogo"
        ordering = ["name"]

    def __str__(self):
        return self.name
