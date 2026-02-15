from django import forms

from apps.invoicing.models.client import CatalogItem


class CatalogItemForm(forms.ModelForm):
    class Meta:
        model = CatalogItem
        fields = [
            "name",
            "description",
            "default_unit_price",
            "default_tax_rate",
            "default_withholding_rate",
            "active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }
