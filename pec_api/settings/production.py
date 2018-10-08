"""
Django production settings for Patate & Cornichon API project.
"""

import os

import django_heroku
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403


# Application definition

INSTALLED_APPS = INSTALLED_APPS + [  # noqa F405
    'algoliasearch_django',
    'storages',
]


# Security configuration

DEBUG = False
SECURE_SSL_REDIRECT = True


# CORS Configuration

CORS_ORIGIN_WHITELIST = (
    'admin.patateetcornichon.com',
)


# Sentry Configuration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN', 'notset'),
    integrations=[DjangoIntegration()],
    send_default_pii=True,
)


# Files configuration

# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEFAULT_FILE_STORAGE
STATICFILES_STORAGE = 'pec_api.storage.StaticRootS3BotoStorage'

# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_STORAGE
DEFAULT_FILE_STORAGE = 'pec_api.storage.MediaRootS3BotoStorage'
THUMBNAIL_DEFAULT_STORAGE = 'pec_api.storage.MediaRootS3BotoStorage'


# Email settings

# See: https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = 'Patate & Cornichon <noreply@testing.patateetcornichon.com>'


# Django Rest Framework Configuration

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)  # noqa: F405 E501


# Heroku Configuration

django_heroku.settings(locals(), staticfiles=False, test_runner=False, logging=False)
