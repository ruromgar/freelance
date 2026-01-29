import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

# Initialize Django ASGI application early to ensure settings are loaded
django_asgi_app = get_asgi_application()
