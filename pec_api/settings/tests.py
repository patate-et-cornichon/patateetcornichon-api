from .base import *  # noqa: F403 F401


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'TEST': {
            'NAME': f"test_{DATABASES['engine']['NAME']}",  # noqa F405
        },
    },
}


# Files configuration

# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_STORAGE
DEFAULT_FILE_STORAGE = 'pec_api.storage.OverwriteStorage'
