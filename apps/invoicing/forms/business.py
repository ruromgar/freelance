from django import forms

from apps.invoicing.models.business import BusinessProfile


class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            "name",
            "tax_id",
            "address",
            "city",
            "postal_code",
            "province",
            "country",
            "phone",
            "email",
            "logo",
            "default_currency",
            "legal_text",
        ]
        widgets = {
            "legal_text": forms.Textarea(attrs={"rows": 3}),
        }
