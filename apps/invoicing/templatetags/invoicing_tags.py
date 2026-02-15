from django import template

from apps.invoicing.models.business import BusinessMembership

register = template.Library()


@register.simple_tag
def has_role(user, business, *roles):
    if not user or not business:
        return False
    membership = BusinessMembership.objects.filter(
        user=user, business_profile=business
    ).first()
    if not membership:
        return False
    return membership.role in roles
