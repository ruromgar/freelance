from django import forms

from apps.fiscal.models import FiscalYear


class FiscalYearForm(forms.ModelForm):
    class Meta:
        model = FiscalYear
        fields = ["year", "estimation_type", "notes"]
        widgets = {
            "year": forms.NumberInput(attrs={"class": "form-input", "min": 2000}),
            "estimation_type": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-textarea", "rows": 3}),
        }
