"""
Django base settings for Patate & Cornichon API project.
"""

import os
from datetime import timedelta
from distutils.util import strtobool

import dj_database_url

import common


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Path of common module
COMMON_PATH = os.path.dirname(common.__file__)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'notset')

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'corsheaders',
    'django_filters',
    'easy_thumbnails',
    'rest_framework',

    # Projects apps,
    'apps.account',
    'apps.comment',
    'apps.recipe',
    'apps.story',
    'common',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pec_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            os.path.join(COMMON_PATH, 'templates'),
        ),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pec_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'engine': dj_database_url.config(conn_max_age=600),
}


# Algolia configuration

ALGOLIA = {
    'APPLICATION_ID': os.environ.get('ALGOLIASEARCH_APPLICATION_ID', 'notset'),
    'API_KEY': os.environ.get('ALGOLIASEARCH_API_KEY', 'notset'),
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_ROOT = 'static'
STATICFILES_DIRS = (
    os.path.join(COMMON_PATH, 'static'),
)
STATIC_URL = '/static/'


# Media files

MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'


# Email settings

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'notset')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'notset')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'notset')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 'notset')
EMAIL_USE_TLS = strtobool(os.environ.get('EMAIL_USE_TLS', 'True'))


# Django Rest Framework Configuration

REST_FRAMEWORK = {
    'DATETIME_FORMAT': '%s',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}


# User configuration

AUTH_USER_MODEL = 'account.User'


# JWT Configuration

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': timedelta(days=2),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'common.drf.jwt.jwt_response_payload_handler',
}


# AWS Settings

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'notset')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'notset')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'notset')
AWS_QUERYSTRING_AUTH = False
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
