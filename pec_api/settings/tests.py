from .base import *  # noqa: F403 F401


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'TEST': {
            'NAME': f"test_{DATABASES['engine']['NAME']}",  # noqa F405
        },
    },
}
