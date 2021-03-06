import uuid

from django.db import models
from django.utils import timezone
from easy_thumbnails.files import get_thumbnailer


class DatedModel(models.Model):
    """ Represents a model associated with created/updated datetime fields.
        An abstract base class model that provides a created and a updated fields to store
        creation date and last updated date.
    """

    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SlugModel(models.Model):
    """ Represents an abstract model used to add a slug field. """

    slug = models.SlugField(max_length=75, unique=True)

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """ Represents an abstract model used to add a published field. """

    published = models.BooleanField(default=False)

    class Meta:
        abstract = True


class PostModel(PublishableModel, SlugModel, DatedModel):
    """ Represents an abstract model used to represent common post attributes. """

    # Custom ID with an UUID instead of the default one
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # We store post titles with a main title and sub title. The full title can not
    # be only the concatenation of the two fields because we want to customize it as we want.
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    full_title = models.CharField(max_length=255, unique=True)

    # SEO fields
    views = models.IntegerField(default=0)
    meta_description = models.TextField()

    class Meta:
        abstract = True
        ordering = ['-created']

    def __str__(self):
        return self.full_title

    @property
    def main_picture(self):
        """ Main picture must be implemented. """
        raise NotImplementedError

    @property
    def main_picture_thumbs(self):
        """ Return cropped main picture with different sizes. """
        sizes = {
            'mini': {'size': (80, 50), 'crop': True},
            'small': {'size': (368, 250), 'crop': True},
            'medium': {'size': (418, 292), 'crop': True},
            'large': {'size': (760, 525), 'crop': True},
            'extra_large': {'size': (1152, 772), 'crop': True},
            '1x1': {'size': (600, 600), 'crop': True},
            '4x3': {'size': (600, 450), 'crop': True},
            '16x9': {'size': (600, 338), 'crop': True},
        }

        thumbnailer = get_thumbnailer(self.main_picture)
        return {
            name: thumbnailer.get_thumbnail(value).url for
            name, value in sizes.items()
        }

    @property
    def comments_count(self):
        """ Return the count of comments linked to the instance. """
        from apps.comment.models import Comment
        return Comment.objects.filter(object_id=self.id, is_valid=True).count()
