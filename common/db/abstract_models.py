from django.db import models


class DatedModel(models.Model):
    """ Represents a model associated with created/updated datetime fields.
        An abstract base class model that provides a created and a updated fields to store
        creation date and last updated date.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SlugModel(models.Model):
    """ Represents am abstract model used to add a slug field. """

    slug = models.SlugField(max_length=75, unique=True)

    class Meta:
        abstract = True
