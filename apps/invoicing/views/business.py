from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.invoicing.forms.business import BusinessProfileForm
from apps.invoicing.models.business import BusinessMembership
from apps.invoicing.services.permissions import get_user_businesses
from apps.invoicing.services.permissions import require_role
from apps.invoicing.services.permissions import set_active_business


@login_required
def business_create(request):
    if request.method == "POST":
        form = BusinessProfileForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save()
            BusinessMembership.objects.create(
                user=request.user,
                business_profile=business,
                role=BusinessMembership.Role.OWNER,
            )
            request.session["active_business_id"] = business.pk
            return redirect("invoicing:dashboard")
    else:
        form = BusinessProfileForm()
    return render(
        request,
        "invoicing/business/create.html",
        {"form": form, "businesses": get_user_businesses(request.user)},
    )


@login_required
@require_role("owner")
def business_edit(request):
    business = request.business
    if request.method == "POST":
        form = BusinessProfileForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            form.save()
            return redirect("invoicing:business_edit")
    else:
        form = BusinessProfileForm(instance=business)
    return render(
        request,
        "invoicing/business/edit.html",
        {
            "form": form,
            "business": business,
            "businesses": get_user_businesses(request.user),
        },
    )


@login_required
@require_role("owner")
def business_delete(request):
    business = request.business
    if request.method == "POST":
        business.delete()
        if "active_business_id" in request.session:
            del request.session["active_business_id"]
        return redirect("invoicing:dashboard")
    return render(
        request,
        "invoicing/business/delete.html",
        {
            "business": business,
            "businesses": get_user_businesses(request.user),
        },
    )


@login_required
def business_switch(request, pk):
    set_active_business(request, pk)
    return redirect("invoicing:dashboard")


@login_required
@require_role("owner")
def business_members(request):
    business = request.business
    memberships = business.memberships.select_related("user").order_by("role")
    if request.method == "POST":
        action = request.POST.get("action")
        membership_id = request.POST.get("membership_id")
        if action == "remove" and membership_id:
            membership = get_object_or_404(
                BusinessMembership, pk=membership_id, business_profile=business
            )
            if membership.user != request.user:
                membership.delete()
        elif action == "change_role" and membership_id:
            new_role = request.POST.get("role")
            membership = get_object_or_404(
                BusinessMembership, pk=membership_id, business_profile=business
            )
            if (
                membership.user != request.user
                and new_role in BusinessMembership.Role.values
            ):
                membership.role = new_role
                membership.save(update_fields=["role"])
        elif action == "invite":
            from django.contrib.auth import get_user_model

            User = get_user_model()
            email = request.POST.get("email", "").strip()
            role = request.POST.get("role", BusinessMembership.Role.VIEWER)
            if email and role in BusinessMembership.Role.values:
                try:
                    user = User.objects.get(email=email)
                    BusinessMembership.objects.get_or_create(
                        user=user,
                        business_profile=business,
                        defaults={"role": role},
                    )
                except User.DoesNotExist:
                    pass
        return redirect("invoicing:business_members")
    return render(
        request,
        "invoicing/business/members.html",
        {
            "business": business,
            "businesses": get_user_businesses(request.user),
            "memberships": memberships,
            "roles": BusinessMembership.Role.choices,
        },
    )
