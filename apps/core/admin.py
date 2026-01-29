from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm
from unfold.forms import UserChangeForm
from unfold.forms import UserCreationForm

from apps.core.models import Profile

admin.site.unregister(User)
admin.site.unregister(Group)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profile"
    ordering_field = ("user__id",)
    fk_name = "user"


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """User admin."""

    inlines = (ProfileInline,)
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_select_related = ("profile",)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """Group admin."""


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "created_at", "updated_at")
    search_fields = ("user__email",)
