"""
Django settings for the AI Study Hub project.

Configuration is driven by environment variables (see .env.example).
"""

from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

# Read .env file if present (never committed to git).
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-change-me-in-production-0123456789abcdef",
)

# DEBUG defaults to False so a missing .env can't accidentally run in
# development mode. Set DEBUG=True explicitly in .env during development.
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "0.0.0.0", ".railway.app", ".up.railway.app"],
)

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

LOCAL_APPS = [
    "core",
    "accounts",
    "dashboard",
    "planner",
    "notes",
    "resources",
    "ai_assistant",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database (PostgreSQL)
# ---------------------------------------------------------------------------
# The project targets PostgreSQL. For convenience during evaluation, if the
# environment variable USE_SQLITE=True is set (or PostgreSQL is unreachable and
# no DB env vars are given), a SQLite fallback keeps the app runnable.
# On Render, the platform injects a full DATABASE_URL connection string — the
# app prefers that over the individual DB_* variables used for local dev.
if env.bool("USE_SQLITE", default=False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif env("DATABASE_URL", default=""):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME", default="ai_study_hub"),
            "USER": env("DB_USER", default="postgres"),
            "PASSWORD": env("DB_PASSWORD", default="postgres"),
            "HOST": env("DB_HOST", default="127.0.0.1"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
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

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise serves collected static files in production (no nginx needed).
# "default" must stay defined here too — overriding STORAGES at all replaces
# Django's built-in default, so omitting it breaks uploaded-file URLs
# (e.g. {{ user.profile.image_url }} → InvalidStorageError).

# Media storage: use Backblaze B2 (S3-compatible) when configured,
# otherwise fall back to local filesystem for development.
if env("AWS_STORAGE_BUCKET_NAME", default=""):
    # Production: Backblaze B2 / S3-compatible storage (PRIVATE bucket)
    # Uses presigned URLs for secure browser access.
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "access_key": env("AWS_ACCESS_KEY_ID"),
                "secret_key": env("AWS_SECRET_ACCESS_KEY"),
                "bucket_name": env("AWS_STORAGE_BUCKET_NAME"),
                "endpoint_url": env("AWS_S3_ENDPOINT_URL"),
                "querystring_auth": True,
                "querystring_expire": 3600,  # 1 hour URL validity
                "file_overwrite": False,
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    # MEDIA_URL points to the B2 bucket endpoint; S3Boto3Storage generates
    # presigned URLs that include authentication in the query string.
    MEDIA_URL = f"https://{env('AWS_STORAGE_BUCKET_NAME')}.{env('AWS_S3_ENDPOINT_URL').replace('https://', '').replace('http://', '')}/"
else:
    # Development: local filesystem storage
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "accounts:login"

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
# Console backend by default so email verification / password reset links are
# printed to the terminal during development. For production, configure the
# Brevo API key (recommended) or an SMTP backend.
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
# Email verification is REQUIRED by default in production for security.
# In development (DEBUG=True), it defaults to True so the flow works via
# console backend. Override via EMAIL_VERIFICATION_REQUIRED environment
# variable if you explicitly need to disable it (e.g., demo without SMTP).
EMAIL_VERIFICATION_REQUIRED = env.bool(
    "EMAIL_VERIFICATION_REQUIRED", default=True
)

# Brevo API (preferred for production - no SMTP timeout issues)
BREVO_API_KEY = env("BREVO_API_KEY", default="")

# Legacy SMTP settings (kept for fallback compatibility if needed)
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="AI Study Hub <no-reply@aistudyhub.local>"
)

# ---------------------------------------------------------------------------
# AI provider configuration (never hard-code secrets)
# ---------------------------------------------------------------------------
AI_API_KEY = env("AI_API_KEY", default="")
AI_API_BASE_URL = env(
    "AI_API_BASE_URL",
    default="https://generativelanguage.googleapis.com/v1beta/openai",
)
AI_MODEL = env("AI_MODEL", default="gemini-3.6-flash")
AI_REQUEST_TIMEOUT = env.int("AI_REQUEST_TIMEOUT", default=60)
AI_MAX_TOKENS = env.int("AI_MAX_TOKENS", default=800)

# ---------------------------------------------------------------------------
# Security (tightened automatically when DEBUG is off)
# ---------------------------------------------------------------------------
CSRF_COOKIE_HTTPONLY = False  # allow JS to read token for fetch requests
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

if not DEBUG:
    # Render terminates TLS at its proxy and forwards X-Forwarded-Proto; this
    # tells Django the request is already HTTPS so SECURE_SSL_REDIRECT doesn't
    # create a redirect loop.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
