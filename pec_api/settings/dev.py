"""
Django development settings for Patate & Cornichon API project.
"""

import django_heroku

from .base import *  # noqa: F403 F401


# Security configuration

DEBUG = True


# Files configuration

# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_STORAGE
DEFAULT_FILE_STORAGE = 'pec_api.storage.OverwriteStorage'


# Heroku Configuration

django_heroku.settings(locals(), staticfiles=False, test_runner=False)
