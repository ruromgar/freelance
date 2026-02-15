from django import forms

from apps.invoicing.models.invoice import Invoice
from apps.invoicing.models.payment import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["invoice", "amount", "date", "method", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, business_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if business_profile:
            self.fields["invoice"].queryset = Invoice.objects.filter(
                business_profile=business_profile
            ).exclude(status=Invoice.Status.CANCELLED)
        self.fields["date"].input_formats = ["%Y-%m-%d"]


class QuickPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "date", "method", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].input_formats = ["%Y-%m-%d"]
