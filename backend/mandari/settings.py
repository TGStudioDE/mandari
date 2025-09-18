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
	"core",
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
		"BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
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
		"rest_framework.authentication.SessionAuthentication",
		"rest_framework.authentication.BasicAuthentication",
	],
	"DEFAULT_PERMISSION_CLASSES": [
		"rest_framework.permissions.IsAuthenticatedOrReadOnly",
	],
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

