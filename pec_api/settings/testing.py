"""
Django testing settings for Patate & Cornichon API project.
"""

import django_heroku

from .base import *  # noqa: F403


# Application definition

INSTALLED_APPS = INSTALLED_APPS + [  # noqa F405
    'raven.contrib.django.raven_compat',
    'storages',
]


# Security configuration

DEBUG = False
SECURE_SSL_REDIRECT = True


# Files configuration

# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEFAULT_FILE_STORAGE
STATICFILES_STORAGE = 'pec_api.storage.StaticRootS3BotoStorage'

# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_STORAGE
DEFAULT_FILE_STORAGE = 'pec_api.storage.MediaRootS3BotoStorage'


# Django Rest Framework Configuration

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)  # noqa: F405 E501


# Heroku Configuration

django_heroku.settings(locals(), staticfiles=False, test_runner=False)
