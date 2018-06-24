"""
Django development settings for Patate & Cornichon API project.
"""

import django_heroku

from .base import *


# Security configuration

DEBUG = True


# Heroku Configuration

django_heroku.settings(locals())
