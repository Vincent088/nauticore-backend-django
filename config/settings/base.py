import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = "django-insecure-nauticore-change-this-in-production"

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "apps.accounts",
    "apps.clients",
    "apps.vessels",
    "apps.materials",
    "apps.progress",
    "apps.documents",
    "apps.maintenance",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
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
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.CustomUser"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "login": "5/minute",
        "register": "10/hour",
    },
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "BLACKLIST_AFTER_ROTATION": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "NautiCore ERP API",
    "DESCRIPTION": "Ship craft company ERP system — vessels, contracts, materials, finance",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


def get_system_theme():
    result = subprocess.run(
        ["defaults", "read", "-g", "AppleInterfaceStyle"],
        capture_output=True,
        text=True,
    )
    return "dark" if "Dark" in result.stdout else "light"


JAZZMIN_SETTINGS = {
    "site_title": "NautiCore ERP",
    "site_header": "NautiCore",
    "site_brand": "NautiCore",
    "welcome_sign": "Welcome to NautiCore ERP",
    "copyright": "NautiCore Ltd",
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "accounts.CustomUser": "fas fa-user-hard-hat",
        "accounts.Profile": "fas fa-id-card",
        "clients.Client": "fas fa-building",
        "clients.ClientContact": "fas fa-address-book",
        "vessels.Vessel": "fas fa-ship",
        "contracts.Contract": "fas fa-file-contract",
        "materials.Material": "fas fa-boxes",
        "progress.Milestone": "fas fa-tasks",
        "documents.Document": "fas fa-file-alt",
        "finance.Invoice": "fas fa-file-invoice-dollar",
        "finance.Payment": "fas fa-money-bill-wave",
    },
    "show_ui_builder": True,
    "related_modal_active": True,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cyborg" if get_system_theme() == "dark" else "flatly",
    "sidebar": (
        "sidebar-dark-primary"
        if get_system_theme() == "dark"
        else "sidebar-light-primary"
    ),
    "navbar": (
        "navbar-dark" if get_system_theme() == "dark" else "navbar-white navbar-light"
    ),
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar_fixed": True,
    "sidebar_fixed": True,
}
