from django import forms

from apps.invoicing.models.business import InvoiceNumbering


class InvoiceNumberingForm(forms.ModelForm):
    class Meta:
        model = InvoiceNumbering
        fields = ["series_prefix", "next_number", "format_pattern"]
