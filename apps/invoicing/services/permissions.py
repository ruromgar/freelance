from functools import wraps

from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.invoicing.models.business import BusinessMembership
from apps.invoicing.models.business import BusinessProfile


def get_user_businesses(user):
    return BusinessProfile.objects.filter(memberships__user=user)


def get_membership(user, business_profile):
    return BusinessMembership.objects.filter(
        user=user, business_profile=business_profile
    ).first()


def get_active_business(request):
    business_id = request.session.get("active_business_id")
    if business_id:
        try:
            business = BusinessProfile.objects.get(pk=business_id)
            if BusinessMembership.objects.filter(
                user=request.user, business_profile=business
            ).exists():
                return business
        except BusinessProfile.DoesNotExist:
            pass
    first = (
        BusinessProfile.objects.filter(memberships__user=request.user)
        .order_by("name")
        .first()
    )
    if first:
        request.session["active_business_id"] = first.pk
    return first


def set_active_business(request, business_id):
    business = get_object_or_404(BusinessProfile, pk=business_id)
    if not BusinessMembership.objects.filter(
        user=request.user, business_profile=business
    ).exists():
        raise Http404
    request.session["active_business_id"] = business.pk
    return business


def require_role(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            business = get_active_business(request)
            if not business:
                from django.shortcuts import redirect

                return redirect("invoicing:business_create")
            membership = get_membership(request.user, business)
            if not membership or membership.role not in roles:
                raise Http404
            request.business = business
            request.membership = membership
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_business(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        business = get_active_business(request)
        if not business:
            from django.shortcuts import redirect

            return redirect("invoicing:business_create")
        membership = get_membership(request.user, business)
        request.business = business
        request.membership = membership
        return view_func(request, *args, **kwargs)

    return wrapper
