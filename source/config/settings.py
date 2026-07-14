import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SERVICE_NAME = os.getenv("SERVICE_NAME", "arna-business-hub")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)
DEBUG = env_bool("DEBUG", ENVIRONMENT == "development")
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,"
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:5174,http://127.0.0.1:5174,"
    "http://localhost:8080,http://127.0.0.1:8080,"
    "http://localhost:4200,http://127.0.0.1:4200",
)
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", False)
CORS_ALLOW_CREDENTIALS = env_bool("CORS_ALLOW_CREDENTIALS", False)
CORS_ALLOW_METHODS = env_list("CORS_ALLOW_METHODS", "DELETE,GET,OPTIONS,PATCH,POST,PUT")
CORS_ALLOW_HEADERS = env_list(
    "CORS_ALLOW_HEADERS",
    "accept,authorization,content-type,origin,user-agent,x-csrftoken,x-requested-with,"
    "x-organization-id,x-user-id,x-plan,x-permissions,x-arna-request-id",
)
CORS_PREFLIGHT_MAX_AGE = int(os.getenv("CORS_PREFLIGHT_MAX_AGE", "86400"))

if os.getenv("VERCEL_URL"):
    ALLOWED_HOSTS.extend([".vercel.app", os.getenv("VERCEL_URL")])
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.getenv('VERCEL_URL')}")

if ENVIRONMENT == "production":
    if DEBUG:
        raise ImproperlyConfigured("DEBUG must be disabled in production.")
    if SECRET_KEY in {"", "replace-me", "dev-only-change-me"}:
        raise ImproperlyConfigured("SECRET_KEY must be set to a strong production value.")
    if JWT_SECRET in {"", "replace-me", "dev-only-change-me"}:
        raise ImproperlyConfigured("JWT_SECRET must be set to the shared production token signing secret.")

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
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "common.middleware.CorsMiddleware",
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
RUNNING_TESTS = any("pytest" in arg or arg == "test" for arg in sys.argv)

if not RUNNING_TESTS and not env_bool("USE_SQLITE") and os.getenv("POSTGRES_HOST"):
    postgres_options = {}
    if os.getenv("POSTGRES_SSLMODE"):
        postgres_options["sslmode"] = os.getenv("POSTGRES_SSLMODE")
    if os.getenv("POSTGRES_CHANNEL_BINDING"):
        postgres_options["channel_binding"] = os.getenv("POSTGRES_CHANNEL_BINDING")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "arna_business_hub_db"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "postgres"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "OPTIONS": postgres_options,
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

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

SESSION_COOKIE_SECURE = ENVIRONMENT == "production"
CSRF_COOKIE_SECURE = ENVIRONMENT == "production"
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", ENVIRONMENT == "production")
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000" if ENVIRONMENT == "production" else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", ENVIRONMENT == "production")
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", ENVIRONMENT == "production")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

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
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "business_hub.schema.add_tenant_id_query_parameter",
    ],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    "SECURITY": [{"bearerAuth": []}],
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
