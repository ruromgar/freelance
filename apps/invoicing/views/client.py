from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.invoicing.forms.client import ClientForm
from apps.invoicing.models.client import Client
from apps.invoicing.services.permissions import get_user_businesses
from apps.invoicing.services.permissions import require_business
from apps.invoicing.services.permissions import require_role


@login_required
@require_business
def client_list(request):
    clients = Client.objects.filter(business_profile=request.business)
    q = request.GET.get("q", "").strip()
    if q:
        clients = clients.filter(name__icontains=q)
    return render(
        request,
        "invoicing/clients/list.html",
        {
            "clients": clients,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "clients",
            "q": q,
        },
    )


@login_required
@require_role("owner", "editor")
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.business_profile = request.business
            client.save()
            return redirect("invoicing:client_list")
    else:
        form = ClientForm()
    return render(
        request,
        "invoicing/clients/create.html",
        {
            "form": form,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "clients",
        },
    )


@login_required
@require_role("owner", "editor")
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk, business_profile=request.business)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("invoicing:client_list")
    else:
        form = ClientForm(instance=client)
    return render(
        request,
        "invoicing/clients/edit.html",
        {
            "form": form,
            "client": client,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "clients",
        },
    )


@login_required
@require_role("owner")
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk, business_profile=request.business)
    if request.method == "POST":
        client.delete()
        return redirect("invoicing:client_list")
    return render(
        request,
        "invoicing/clients/delete.html",
        {
            "client": client,
            "business": request.business,
            "businesses": get_user_businesses(request.user),
            "active_section": "clients",
        },
    )
