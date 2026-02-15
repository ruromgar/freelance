from django import forms

from apps.fiscal.models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "date",
            "concept",
            "supplier",
            "reference",
            "category",
            "taxable_base",
            "vat_type",
            "irpf_deductible",
            "vat_deductible",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-input"},
            ),
            "concept": forms.TextInput(attrs={"class": "form-input"}),
            "supplier": forms.TextInput(attrs={"class": "form-input"}),
            "reference": forms.TextInput(attrs={"class": "form-input"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "taxable_base": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01"}
            ),
            "vat_type": forms.Select(attrs={"class": "form-select"}),
            "irpf_deductible": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "vat_deductible": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "notes": forms.Textarea(attrs={"class": "form-textarea", "rows": 3}),
        }
