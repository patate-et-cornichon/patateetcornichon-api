"""
Django development settings for Patate & Cornichon API project.
"""

import django_heroku

from .base import *  # noqa: F403 F401


# Security configuration

DEBUG = True


# Heroku Configuration

django_heroku.settings(locals(), staticfiles=False, test_runner=False)
