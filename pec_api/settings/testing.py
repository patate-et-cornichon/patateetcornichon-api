"""
Django testing settings for Patate & Cornichon API project.
"""

import django_heroku

from .base import *


# Security configuration

DEBUG = False
SECURE_SSL_REDIRECT = True


# Django Rest Framework Configuration

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)


# Heroku Configuration

django_heroku.settings(locals())
