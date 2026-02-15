from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path

from apps.fiscal import urls as fiscal_urls
from apps.invoicing import urls as invoicing_urls

urlpatterns = [
    # Login and logout
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),
    # Admin
    path("room/", admin.site.urls),
    # Apps
    path("", include(invoicing_urls)),
    path("fiscal/", include(fiscal_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
