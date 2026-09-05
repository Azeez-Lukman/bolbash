"""
Django settings for Bolbash Beauty Spot project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env', override=True)

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-bolbash-beauty-spot-default-key')

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

# Host and Domain Configuration
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',') if host.strip()]
if '.onrender.com' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.extend(['.onrender.com', 'hairbybolbash.onrender.com'])

# Automatic Render Hostname Detection
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# CSRF Trusted Origins Configuration
CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS 
    if host not in ('localhost', '127.0.0.1', 'testserver') and not host.startswith('.')
]
CSRF_TRUSTED_ORIGINS.extend(['https://*.onrender.com', 'https://hairbybolbash.onrender.com'])
env_csrf = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if env_csrf:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in env_csrf.split(',') if origin.strip()])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Project Custom Apps
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'booking.apps.BookingConfig',
    'academy.apps.AcademyConfig',
    'blog.apps.BlogConfig',
    'shop.apps.ShopConfig',
    'payments.apps.PaymentsConfig',
    'notifications.apps.NotificationsConfig',
    'admin_panel.apps.AdminPanelConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'core.context_processors.bank_details',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database Configuration - MySQL Backend with DATABASE_URL & Environment Support
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

import dj_database_url

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            engine='django.db.backends.mysql'
        )
    }
    DATABASES['default'].setdefault('OPTIONS', {})
    DATABASES['default']['OPTIONS'].setdefault('init_command', "SET sql_mode='STRICT_TRANS_TABLES'")
    DATABASES['default']['OPTIONS'].setdefault('charset', 'utf8mb4')
else:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
            'NAME': os.getenv('DB_NAME', 'bolbash_beautyspot_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'root'),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images) & Whitenoise Compression
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = Path(os.getenv('STATIC_ROOT', BASE_DIR / 'staticfiles'))

# Whitenoise production static file storage with compression & caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (Uploaded images, resources)
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.getenv('MEDIA_ROOT', BASE_DIR / 'media'))

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Paystack Gateway & Settlement Bank Settings
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY', 'pk_test_45ac4546609405d68991dc72b77ba25649bd8103')
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY', 'sk_test_c39ac295aa0b82515f36239b3c7cae9dda5cb2a9')
PAYSTACK_PAYMENT_URL = os.getenv('PAYSTACK_PAYMENT_URL', 'https://api.paystack.co')
PAYSTACK_BANK_NAME = os.getenv('PAYSTACK_BANK_NAME', 'OPay')
PAYSTACK_ACCOUNT_NUMBER = os.getenv('PAYSTACK_ACCOUNT_NUMBER', '8148281423')
PAYSTACK_ACCOUNT_NAME = os.getenv('PAYSTACK_ACCOUNT_NAME', 'Lukexx Business And Technology')

# Testing Upfront Booking Deposit Limit
BOOKING_DEPOSIT_AMOUNT = float(os.getenv('BOOKING_DEPOSIT_AMOUNT', '100.00'))

# Email Notification System Settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Bolbash Beauty Spot <no-reply@bolbashbeautyspot.com>')

# Security & Production Deployment Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True



