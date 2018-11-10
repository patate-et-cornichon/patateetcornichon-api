from django.views.decorators.cache import cache_page


class CacheMixin:
    """ Caches retrieve and list methods for non-admin users only. """

    cache_timeout = None

    def retrieve(self, *args, **kwargs):
        """ Active cache behavior only for non-admin users. """
        if self.request.user.is_superuser:
            return super().retrieve(*args, **kwargs)
        else:
            return cache_page(self.cache_timeout)(super().retrieve)(*args, **kwargs)

    def list(self, *args, **kwargs):
        """ Active cache behavior only for non-admin users. """
        if self.request.user.is_superuser:
            return super().list(*args, **kwargs)
        else:
            return cache_page(self.cache_timeout)(super().list)(*args, **kwargs)
