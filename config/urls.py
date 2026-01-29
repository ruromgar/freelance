from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path

from apps.freelance import urls as freelance_urls

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
    path("", include(freelance_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
