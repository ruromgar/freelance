from django.conf import settings
from django.db import models


class BusinessProfile(models.Model):
    name = models.CharField("Nombre", max_length=255)
    tax_id = models.CharField("NIF/CIF", max_length=20)
    address = models.CharField("Dirección", max_length=255, blank=True)
    city = models.CharField("Ciudad", max_length=100, blank=True)
    postal_code = models.CharField("Código postal", max_length=10, blank=True)
    province = models.CharField("Provincia", max_length=100, blank=True)
    country = models.CharField("País", max_length=2, default="ES")
    phone = models.CharField("Teléfono", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    logo = models.ImageField("Logo", upload_to="logos/", blank=True)
    default_currency = models.CharField(
        "Moneda por defecto", max_length=3, default="EUR"
    )
    legal_text = models.TextField("Texto legal", blank=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Fecha de actualización", auto_now=True)

    class Meta:
        verbose_name = "Perfil de empresa"
        verbose_name_plural = "Perfiles de empresa"
        ordering = ["name"]

    def __str__(self):
        return self.name


class BusinessMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Propietario"
        EDITOR = "editor", "Editor"
        VIEWER = "viewer", "Lector"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business_memberships",
        verbose_name="Usuario",
    )
    business_profile = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="Empresa",
    )
    role = models.CharField(
        "Rol", max_length=10, choices=Role.choices, default=Role.VIEWER
    )
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
        unique_together = ("user", "business_profile")

    def __str__(self):
        return f"{self.user} → {self.business_profile} ({self.get_role_display()})"


class InvoiceNumbering(models.Model):
    business_profile = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="numbering_configs",
        verbose_name="Empresa",
    )
    series_prefix = models.CharField("Prefijo de serie", max_length=10, default="F")
    next_number = models.PositiveIntegerField("Siguiente número", default=1)
    format_pattern = models.CharField(
        "Patrón de formato",
        max_length=100,
        default="{prefix}-{year}-{number:05d}",
    )

    class Meta:
        verbose_name = "Numeración de facturas"
        verbose_name_plural = "Numeraciones de facturas"

    def __str__(self):
        return f"{self.business_profile} – {self.series_prefix}"

    def generate_number(self, year):
        number = self.format_pattern.format(
            prefix=self.series_prefix,
            year=year,
            number=self.next_number,
        )
        self.next_number += 1
        self.save(update_fields=["next_number"])
        return number


class InvoiceTheme(models.Model):
    class FontFamily(models.TextChoices):
        SANS_SERIF = "sans-serif", "Sans-serif"
        SERIF = "serif", "Serif"
        MONOSPACE = "monospace", "Monospace"

    class LayoutVariant(models.TextChoices):
        CLASSIC = "classic", "Clásico"
        MODERN = "modern", "Moderno"
        MINIMAL = "minimal", "Minimalista"

    business_profile = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="themes",
        verbose_name="Empresa",
    )
    name = models.CharField("Nombre", max_length=100)
    primary_color = models.CharField("Color primario", max_length=7, default="#1e3a5f")
    secondary_color = models.CharField(
        "Color secundario", max_length=7, default="#f0f4f8"
    )
    font_family = models.CharField(
        "Tipografía",
        max_length=20,
        choices=FontFamily.choices,
        default=FontFamily.SANS_SERIF,
    )
    layout_variant = models.CharField(
        "Variante de diseño",
        max_length=10,
        choices=LayoutVariant.choices,
        default=LayoutVariant.CLASSIC,
    )
    is_default = models.BooleanField("Por defecto", default=False)

    class Meta:
        verbose_name = "Tema de factura"
        verbose_name_plural = "Temas de factura"

    def __str__(self):
        return f"{self.name} ({self.business_profile})"

    def save(self, *args, **kwargs):
        if self.is_default:
            InvoiceTheme.objects.filter(
                business_profile=self.business_profile, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
