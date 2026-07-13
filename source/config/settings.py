import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SERVICE_NAME = os.getenv("SERVICE_NAME", "arna-business-hub")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
DEBUG = env_bool("DEBUG", ENVIRONMENT == "development")
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "business_hub",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "business_hub.middleware.TenantContextMiddleware",
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
ASGI_APPLICATION = "config.asgi.application"

if os.getenv("POSTGRES_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "arna_business_hub_db"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "postgres"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Arna Business Hub API",
    "DESCRIPTION": (
        "Business Hub Service API for Bisnis Naik Kelas: roadmap, checklist, "
        "Business Vault metadata, score, gamification, goals, calendar, AI insights, "
        "and integration status."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v1/business-hub",
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
    },
}

DEV_AUTH_BYPASS = env_bool("DEV_AUTH_BYPASS", ENVIRONMENT != "production")
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "IDR")
SCORE_CALCULATION_VERSION = int(os.getenv("SCORE_CALCULATION_VERSION", "1"))
AI_CONTEXT_MAX_TOKENS = int(os.getenv("AI_CONTEXT_MAX_TOKENS", "8000"))
AI_MONTHLY_INSIGHT_DEFAULT_QUOTA = os.getenv("AI_MONTHLY_INSIGHT_DEFAULT_QUOTA", "10")

EXTERNAL_SERVICES = {
    "sso": os.getenv("SSO_BASE_URL", "https://sso.arnatech.id"),
    "commerce": os.getenv("COMMERCE_BASE_URL", "https://product.arnatech.id/api/v1"),
    "file_manager": os.getenv("FILE_MANAGER_BASE_URL", "https://storage.arnatech.id"),
    "website": os.getenv("WEBSITE_SERVICE_BASE_URL", "https://bisnisnaikkelas.com/api/v1"),
    "accounting": os.getenv("ACCOUNTING_SERVICE_BASE_URL", "https://accounting.bisnisnaikkelas.com/api/v1"),
    "notification": os.getenv("NOTIFICATION_SERVICE_BASE_URL", "https://notification.arnatech.id/api/v1"),
    "ai_gateway": os.getenv("AI_GATEWAY_BASE_URL", "https://ai.arnatech.id/api/v1"),
}
