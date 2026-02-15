from django import forms

from apps.invoicing.models.client import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "name",
            "tax_id",
            "address",
            "city",
            "postal_code",
            "province",
            "email",
            "phone",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
