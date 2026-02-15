from django import forms

from apps.invoicing.models.business import InvoiceTheme


class InvoiceThemeForm(forms.ModelForm):
    class Meta:
        model = InvoiceTheme
        fields = [
            "name",
            "primary_color",
            "secondary_color",
            "font_family",
            "layout_variant",
            "is_default",
        ]
        widgets = {
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
        }
