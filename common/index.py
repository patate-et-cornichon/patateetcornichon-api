import algoliasearch_django


def save_record(instance, **kwargs):  # pragma: no cover
    """ Check if Algolia is installed and update index. """
    from django.conf import settings
    if 'algoliasearch_django' in settings.INSTALLED_APPS:
        algoliasearch_django.save_record(instance, **kwargs)
