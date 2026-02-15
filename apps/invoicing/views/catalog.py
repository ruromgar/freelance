from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.invoicing.forms.catalog import CatalogItemForm
from apps.invoicing.models.client import CatalogItem
from apps.invoicing.services.permissions import get_user_businesses
from apps.invoicing.services.permissions import require_business
from apps.invoicing.services.permissions import require_role


@login_required
@require_business
def catalog_list(request):
    items = CatalogItem.objects.filter(business_profile=request.business)
    show_inactive = request.GET.get("inactive") == "1"
    if not show_inactive:
        items = items.filter(active=True)
    return render(
        request,
        "invoicing/catalog/list.html",
        {
            "items": items,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "catalog",
            "show_inactive": show_inactive,
        },
    )


@login_required
@require_role("owner", "editor")
def catalog_create(request):
    if request.method == "POST":
        form = CatalogItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.business_profile = request.business
            item.save()
            return redirect("invoicing:catalog_list")
    else:
        form = CatalogItemForm()
    return render(
        request,
        "invoicing/catalog/form.html",
        {
            "form": form,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "catalog",
            "title": "Nuevo artículo",
        },
    )


@login_required
@require_role("owner", "editor")
def catalog_edit(request, pk):
    item = get_object_or_404(CatalogItem, pk=pk, business_profile=request.business)
    if request.method == "POST":
        form = CatalogItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("invoicing:catalog_list")
    else:
        form = CatalogItemForm(instance=item)
    return render(
        request,
        "invoicing/catalog/form.html",
        {
            "form": form,
            "item": item,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "catalog",
            "title": f"Editar: {item.name}",
        },
    )


@login_required
@require_role("owner")
def catalog_delete(request, pk):
    item = get_object_or_404(CatalogItem, pk=pk, business_profile=request.business)
    if request.method == "POST":
        item.delete()
        return redirect("invoicing:catalog_list")
    return render(
        request,
        "invoicing/catalog/delete.html",
        {
            "item": item,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "catalog",
        },
    )


@login_required
@require_business
def catalog_json(request):
    items = CatalogItem.objects.filter(
        business_profile=request.business, active=True
    ).values(
        "pk",
        "name",
        "description",
        "default_unit_price",
        "default_tax_rate",
        "default_withholding_rate",
    )
    return JsonResponse(list(items), safe=False)
