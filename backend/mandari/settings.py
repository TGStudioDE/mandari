import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"rest_framework",
	"drf_spectacular",
	"django_filters",
	"corsheaders",
	"django_prometheus",
	"core",
]

MIDDLEWARE = [
	"django_prometheus.middleware.PrometheusBeforeMiddleware",
	"django.middleware.security.SecurityMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"corsheaders.middleware.CorsMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mandari.tenant_middleware.TenantMiddleware",
	"mandari.request_id.RequestIdMiddleware",
	"django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "mandari.urls"

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
			],
		},
	}
]

WSGI_APPLICATION = "mandari.wsgi.application"

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.postgresql",
		"NAME": os.getenv("POSTGRES_DB", "mandari"),
		"USER": os.getenv("POSTGRES_USER", "mandari"),
		"PASSWORD": os.getenv("POSTGRES_PASSWORD", "mandari"),
		"HOST": os.getenv("POSTGRES_HOST", "localhost"),
		"PORT": os.getenv("POSTGRES_PORT", "5432"),
	}
}

CACHES = {
	"default": {
		"BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
		"LOCATION": f"{os.getenv('MEMCACHED_HOST', 'localhost')}:{os.getenv('MEMCACHED_PORT', '11211')}",
	}
}

AUTH_USER_MODEL = "core.User"

REST_FRAMEWORK = {
	"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
	"DEFAULT_FILTER_BACKENDS": [
		"django_filters.rest_framework.DjangoFilterBackend",
	],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "core.auth.CsrfExemptSessionAuthentication",
    ],
	"DEFAULT_PERMISSION_CLASSES": [
		"rest_framework.permissions.IsAuthenticatedOrReadOnly",
	],
	"DEFAULT_THROTTLE_CLASSES": [
		"rest_framework.throttling.AnonRateThrottle",
		"rest_framework.throttling.UserRateThrottle",
	],
	"DEFAULT_THROTTLE_RATES": {
		"anon": os.getenv("DRF_THROTTLE_ANON", "100/min"),
		"user": os.getenv("DRF_THROTTLE_USER", "1000/min"),
	},
}

SPECTACULAR_SETTINGS = {
	"TITLE": "Mandari API",
	"DESCRIPTION": "MVP API für Mandari",
	"VERSION": "0.1.0",
}

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Storage (S3/MinIO)
if os.getenv("S3_ENDPOINT_URL"):
	INSTALLED_APPS.append("storages")
	DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
	AWS_S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
	AWS_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY")
	AWS_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_KEY")
	AWS_STORAGE_BUCKET_NAME = os.getenv("S3_BUCKET")
	AWS_S3_REGION_NAME = os.getenv("S3_REGION", "eu-central-1")
	AWS_S3_SIGNATURE_VERSION = "s3v4"

# OpenSearch
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))

# E-Mail
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@mandari.local")

# Frontend Basis-URL (für Double-Opt-In Links)
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:4321")

# CORS
CORS_ALLOWED_ORIGINS = [o for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o]
if not CORS_ALLOWED_ORIGINS and DEBUG:
	CORS_ALLOW_ALL_ORIGINS = True
else:
	CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "True") == "True"

# Security Headers
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "False") == "True"
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "False") == "True"
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False") == "True"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Cookies/CSRF
CSRF_TRUSTED_ORIGINS = [o for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o]
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False") == "True"

