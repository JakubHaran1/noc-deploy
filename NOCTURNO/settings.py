import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-...'
DEBUG = True
ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'APP',
    'django.contrib.postgres'
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'NOCTURNO.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'NOCTURNO.wsgi.application'


DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://noc_q79c_user:HetTcmEFElz6wLBTMU1yMnPQQnIxoWF7@dpg-d40nthali9vc73bqclog-a/noc_q79c',
        conn_max_age=600
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Podstawowe
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Dane dostępowe do Cloudflare R2
AWS_ACCESS_KEY_ID = "9dbc33192d8eb3a3482162ef345496b2"
AWS_SECRET_ACCESS_KEY = "b1c6b95c4b73d3ba233cbf66a1697a32404a57b9aacba3dd3ff9359b65c3be5b"


AWS_STORAGE_BUCKET_NAME = "nocturno-media"


AWS_S3_ENDPOINT_URL = "https://52c2b890f8b53afb374341eaa6646845.r2.cloudflarestorage.com"


MEDIA_URL = "https://media.nocturno.click/"

MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = "APP.PartyUser"

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

# ustawienia email
EMAIL_BACKEND = 'NOCTURNO.email_backend.NocturnoEmailBackend'
RESEND_SMTP_PORT = 587
RESEND_SMTP_USERNAME = 'resend'
RESEND_SMTP_HOST = 'smtp.resend.com'
