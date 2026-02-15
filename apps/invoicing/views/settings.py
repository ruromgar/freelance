from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.invoicing.forms.theme import InvoiceThemeForm
from apps.invoicing.models.business import InvoiceTheme
from apps.invoicing.services.permissions import get_user_businesses
from apps.invoicing.services.permissions import require_role


@login_required
@require_role("owner")
def theme_list(request):
    themes = InvoiceTheme.objects.filter(business_profile=request.business)
    return render(
        request,
        "invoicing/settings/theme_list.html",
        {
            "themes": themes,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "settings_theme",
        },
    )


@login_required
@require_role("owner")
def theme_create(request):
    if request.method == "POST":
        form = InvoiceThemeForm(request.POST)
        if form.is_valid():
            theme = form.save(commit=False)
            theme.business_profile = request.business
            theme.save()
            return redirect("invoicing:theme_list")
    else:
        form = InvoiceThemeForm()
    return render(
        request,
        "invoicing/settings/theme_form.html",
        {
            "form": form,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "settings_theme",
            "title": "Nuevo tema",
        },
    )


@login_required
@require_role("owner")
def theme_edit(request, pk):
    theme = get_object_or_404(InvoiceTheme, pk=pk, business_profile=request.business)
    if request.method == "POST":
        form = InvoiceThemeForm(request.POST, instance=theme)
        if form.is_valid():
            form.save()
            return redirect("invoicing:theme_list")
    else:
        form = InvoiceThemeForm(instance=theme)
    return render(
        request,
        "invoicing/settings/theme_form.html",
        {
            "form": form,
            "theme": theme,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "settings_theme",
            "title": f"Editar tema: {theme.name}",
        },
    )


@login_required
@require_role("owner")
def theme_delete(request, pk):
    theme = get_object_or_404(InvoiceTheme, pk=pk, business_profile=request.business)
    if request.method == "POST":
        theme.delete()
        return redirect("invoicing:theme_list")
    return render(
        request,
        "invoicing/settings/theme_delete.html",
        {
            "theme": theme,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "settings_theme",
        },
    )
