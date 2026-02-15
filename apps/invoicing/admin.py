from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline

from apps.invoicing.models.business import BusinessMembership
from apps.invoicing.models.business import BusinessProfile
from apps.invoicing.models.business import InvoiceNumbering
from apps.invoicing.models.business import InvoiceTheme
from apps.invoicing.models.client import CatalogItem
from apps.invoicing.models.client import Client
from apps.invoicing.models.invoice import Invoice
from apps.invoicing.models.invoice import InvoiceLineItem
from apps.invoicing.models.payment import Payment


class BusinessMembershipInline(TabularInline):
    model = BusinessMembership
    extra = 1


class InvoiceNumberingInline(TabularInline):
    model = InvoiceNumbering
    extra = 0


class InvoiceThemeInline(TabularInline):
    model = InvoiceTheme
    extra = 0


@admin.register(BusinessProfile)
class BusinessProfileAdmin(ModelAdmin):
    list_display = ("name", "tax_id", "city", "email")
    search_fields = ("name", "tax_id")
    inlines = [BusinessMembershipInline, InvoiceNumberingInline, InvoiceThemeInline]


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = ("name", "tax_id", "business_profile", "email")
    list_filter = ("business_profile",)
    search_fields = ("name", "tax_id")


@admin.register(CatalogItem)
class CatalogItemAdmin(ModelAdmin):
    list_display = ("name", "default_unit_price", "default_tax_rate", "active")
    list_filter = ("business_profile", "active")


class InvoiceLineItemInline(TabularInline):
    model = InvoiceLineItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ("number", "client", "status", "issue_date", "currency")
    list_filter = ("status", "business_profile")
    search_fields = ("number", "client__name")
    inlines = [InvoiceLineItemInline]


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ("invoice", "amount", "date", "method")
    list_filter = ("method",)
