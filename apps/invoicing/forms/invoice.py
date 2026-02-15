from django import forms
from django.forms import inlineformset_factory

from apps.invoicing.models.client import Client
from apps.invoicing.models.invoice import Invoice
from apps.invoicing.models.invoice import InvoiceLineItem


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "client",
            "issue_date",
            "due_date",
            "currency",
            "notes",
            "legal_text",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 2}),
            "legal_text": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, business_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if business_profile:
            self.fields["client"].queryset = Client.objects.filter(
                business_profile=business_profile
            )
        self.fields["issue_date"].input_formats = ["%Y-%m-%d"]
        self.fields["due_date"].input_formats = ["%Y-%m-%d"]


class InvoiceLineItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceLineItem
        fields = [
            "description",
            "quantity",
            "unit_price",
            "tax_rate",
            "withholding_rate",
            "discount_percent",
            "position",
        ]
        widgets = {
            "description": forms.TextInput(attrs={"placeholder": "Descripción"}),
            "position": forms.HiddenInput(),
        }


InvoiceLineItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceLineItem,
    form=InvoiceLineItemForm,
    extra=1,
    can_delete=True,
)
