import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models

from common.db.abstract_models import DatedModel


class Comment(DatedModel):
    """ Represents a comment.
        A comment can be associated to another model (like Recipe or Blog).
    """

    # Custom ID with an UUID instead of the default one
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    is_valid = models.BooleanField(default=False)

    # A user can post a comment as a classic user or can be unregistered.
    registered_author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE,
    )
    unregistered_author = JSONField(null=True)

    # An author can be notified when another user post a response in the conversation
    be_notified = models.BooleanField(default=False)

    content = models.TextField()

    # The comment needs to be associated with another specific model identified by its ID.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    commented_object = GenericForeignKey('content_type', 'object_id')

    parent = models.ForeignKey(
        'self', null=True, related_name='children', on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'Comment from {self.author.email}'

    @property
    def author(self):
        """ Get the author instance. """
        return self.registered_author or self.unregistered_author

    def clean(self):
        # Don't allow comment without author.
        if self.registered_author is None and self.unregistered_author is None:
            raise ValidationError('An author needs to be assigned.')
