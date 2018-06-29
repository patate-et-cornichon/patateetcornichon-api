import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


class MediaRootS3BotoStorage(S3Boto3Storage):
    """ Overwrite the default S3 System Storage in order to indicate
        a media files location.
    """
    location = 'media'


class StaticRootS3BotoStorage(S3Boto3Storage):
    """ Overwrite the default S3 System Storage in order to indicate
        a static files location.
    """
    location = 'static'


class OverwriteStorage(FileSystemStorage):
    """ Overwrite the default FileSystemStorage provided by Django. """

    def get_available_name(self, name, max_length=None):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
