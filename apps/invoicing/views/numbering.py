from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from apps.invoicing.forms.numbering import InvoiceNumberingForm
from apps.invoicing.models.business import InvoiceNumbering
from apps.invoicing.services.permissions import get_user_businesses
from apps.invoicing.services.permissions import require_role


@login_required
@require_role("owner")
def numbering_settings(request):
    numbering, _ = InvoiceNumbering.objects.get_or_create(
        business_profile=request.business,
        defaults={"series_prefix": "F", "next_number": 1},
    )
    if request.method == "POST":
        form = InvoiceNumberingForm(request.POST, instance=numbering)
        if form.is_valid():
            form.save()
            return redirect("invoicing:numbering_settings")
    else:
        form = InvoiceNumberingForm(instance=numbering)
    # Preview
    preview = numbering.format_pattern.format(
        prefix=numbering.series_prefix,
        year=2026,
        number=numbering.next_number,
    )
    return render(
        request,
        "invoicing/settings/numbering.html",
        {
            "form": form,
            "numbering": numbering,
            "preview": preview,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "settings_numbering",
        },
    )
