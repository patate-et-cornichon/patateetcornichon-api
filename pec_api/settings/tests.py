from .base import *  # noqa: F403 F401


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'TEST': {
            'NAME': f"test_{DATABASES['engine']['NAME']}",  # noqa F405
        },
    },
}


# Cache configuration

# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

CACHE_MIDDLEWARE_SECONDS = 60 * 60 * 24  # One day


# Files configuration

# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_STORAGE
DEFAULT_FILE_STORAGE = 'pec_api.storage.OverwriteStorage'
