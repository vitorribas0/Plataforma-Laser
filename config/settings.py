import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
# `vercel pull` writes `.env.local`; local Docker/dev setups use `.env`. Neither
# overrides real process env vars (e.g. those injected by Vercel at runtime).
load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-insecure-key")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host.strip()]
if os.getenv("VERCEL"):
    # Covers the production domain, the project's own preview domain, and every
    # branch/PR preview under *.vercel.app.
    ALLOWED_HOSTS.append(".vercel.app")
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
if os.getenv("VERCEL"):
    CSRF_TRUSTED_ORIGINS.append("https://*.vercel.app")
# Vercel terminates TLS at the edge and forwards over HTTP internally; without this,
# request.is_secure() is always False behind the proxy and SECURE_SSL_REDIRECT loops.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "widget_tweaks", "core", "tenants", "users", "clients", "laser", "dashboard",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.TenantMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True, "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages", "core.context_processors.tenant_context"]}}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql", "NAME": os.getenv("POSTGRES_DB", "plataforma_laser"), "USER": os.getenv("POSTGRES_USER", "plataforma"), "PASSWORD": os.getenv("POSTGRES_PASSWORD", "plataforma"), "HOST": os.getenv("POSTGRES_HOST", "localhost"), "PORT": os.getenv("POSTGRES_PORT", "5432")}}

# DATABASE_URL is a manual override (e.g. exported locally with Supabase's direct,
# non-pooled URL to run `manage.py migrate`). POSTGRES_URL is what the Vercel
# Supabase integration injects automatically at runtime: a pgbouncer connection in
# transaction-pooling mode, which is what Vercel Functions should use.
database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
if database_url:
    DATABASES = {"default": dj_database_url.parse(database_url, conn_max_age=600)}
    # Transaction-mode pgbouncer doesn't support server-side prepared statements or
    # named cursors: psycopg3 auto-prepares repeated queries by default, which then
    # errors ("prepared statement ... does not exist") once pgbouncer hands the
    # underlying connection to a different session. Both must be disabled.
    DATABASES["default"]["OPTIONS"] = {"prepare_threshold": None}
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

if os.getenv("DJANGO_TESTING", "False").lower() == "true":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test.sqlite3"}}
AUTH_USER_MODEL = "users.User"
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Media (client photos) lives in a private Supabase Storage bucket in production,
# since Vercel Functions have a read-only/ephemeral filesystem. Falls back to local
# disk storage (Django's default) for local dev when Supabase env vars aren't set.
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "media")
SUPABASE_STORAGE_SIGNED_URL_EXPIRY = int(os.getenv("SUPABASE_STORAGE_SIGNED_URL_EXPIRY", "3600"))
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    DEFAULT_FILE_STORAGE = "core.storage.SupabaseMediaStorage"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
