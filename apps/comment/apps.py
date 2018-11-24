from django.apps import AppConfig


class CommentConfig(AppConfig):
    label = 'comment'
    name = 'apps.comment'

    def ready(self):
        """ Executes whatever is necessary when the application is ready. """
        from . import receivers  # noqa: F401
