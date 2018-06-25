"""
    Common abstract models
    ======================
    This module defines common abstract models that can be used (or combined) when defining new
    models.
"""

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
