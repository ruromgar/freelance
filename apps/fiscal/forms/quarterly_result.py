from django import forms

from apps.fiscal.models import QuarterlyResult


class QuarterlyResultForm(forms.ModelForm):
    class Meta:
        model = QuarterlyResult
        fields = [
            "modelo_303_submitted",
            "modelo_130_submitted",
            "submission_date",
            "notes",
        ]
        widgets = {
            "modelo_303_submitted": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01"}
            ),
            "modelo_130_submitted": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01"}
            ),
            "submission_date": forms.DateInput(
                attrs={"type": "date", "class": "form-input"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-textarea", "rows": 3}),
        }
