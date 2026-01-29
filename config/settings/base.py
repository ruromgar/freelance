import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# change to .env.prod for production !!!
env_file = os.getenv("ENV_FILE", ".env")

load_dotenv(BASE_DIR / env_file)


SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "False") in ["True", "true", "1", "yes", "y"]
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    # My apps
    "apps.freelance",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "apps" / "core" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

DB_ENGINE = os.getenv("DB_ENGINE", None)
DB_USERNAME = os.getenv("DB_USERNAME", None)
DB_PASS = os.getenv("DB_PASS", None)
DB_HOST = os.getenv("DB_HOST", None)
DB_PORT = os.getenv("DB_PORT", None)
DB_NAME = os.getenv("DB_NAME", None)

# Whitelist of allowed database engines
ALLOWED_DB_ENGINES = {"sqlite3", "postgresql", "mysql"}

if DB_ENGINE and DB_NAME and DB_USERNAME:
    if DB_ENGINE not in ALLOWED_DB_ENGINES:
        raise ImproperlyConfigured(f"Invalid DB_ENGINE: {DB_ENGINE}")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends." + DB_ENGINE,
            "NAME": DB_NAME,
            "USER": DB_USERNAME,
            "PASSWORD": DB_PASS,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "data", "db", "db.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = "/staticfiles/"
MEDIA_URL = "/media/"
MEDIA_ROOT = Path("/data/library")

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "freelance:index"
LOGOUT_REDIRECT_URL = "login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache (file-based)
# DATA_DIR: local dev uses .data/, Docker mounts to /app/data
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / ".data"))
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": DATA_DIR / "cache",
    }
}

# Security settings
SESSION_COOKIE_HTTPONLY = True  # Prevent JS access to session cookie
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME sniffing
X_FRAME_OPTIONS = "DENY"  # Clickjacking protection

UNFOLD = {
    "SITE_TITLE": "Freelance Admin",
    "SITE_HEADER": "Freelance - Administración",
    "SITE_URL": "/",
    "SHOW_COUNTS": True,
    "SHOW_HISTORY": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Ir a la aplicación",
                "items": [
                    {"title": "Volver al inicio", "link": "/"},
                ],
            },
            {
                "title": "Autenticación",
                "items": [
                    {"title": "Usuarios", "link": "/room/auth/user/"},
                    {"title": "Grupos", "link": "/room/auth/group/"},
                ],
            },
            {
                "title": "Core",
                "items": [
                    {"title": "Perfiles", "link": "/room/core/profile/"},
                ],
            },
            {
                "title": "Freelance",
                "items": [
                    {"title": "Años fiscales", "link": "/room/freelance/fiscalyear/"},
                    {"title": "Trimestres", "link": "/room/freelance/quarter/"},
                    {"title": "Ingresos", "link": "/room/freelance/income/"},
                    {"title": "Gastos", "link": "/room/freelance/expense/"},
                    {"title": "Resultados trimestrales", "link": "/room/freelance/quarterlyresult/"},
                ],
            },
        ],
    },
}
