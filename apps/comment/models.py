import uuid
from collections import namedtuple

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
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
    )
    unregistered_author = JSONField(blank=True, null=True)

    # An author can be notified when another user post a response in the conversation
    be_notified = models.BooleanField(default=False)

    content = models.TextField()

    # The comment needs to be associated with another specific model identified by its ID.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    commented_object = GenericForeignKey('content_type', 'object_id')

    parent = models.ForeignKey(
        'self', blank=True, null=True, related_name='children', on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Comment from {self.author.email if self.author else "unknown author"}'

    def clean(self):
        # Don't allow comment without author.
        if self.registered_author is None and self.unregistered_author is None:
            raise ValidationError('An author needs to be assigned.')

    @property
    def author(self):
        """ Get the author instance. """
        if self.registered_author is not None or self.unregistered_author is not None:
            if self.registered_author:
                return self.registered_author

            # Create a namedtuple for unregistered author
            unregistered_author_namedtuple = namedtuple(
                'UnregisteredAuthor',
                self.unregistered_author.keys()
            )
            unregistered_author = unregistered_author_namedtuple(*self.unregistered_author.values())
            return unregistered_author

    def get_subscribers(self):
        """ Get a list of all email to be notified when an answer is published. """
        email_list = []
        if self.parent is not None:
            parent_email = self.parent.author.email
            if self.parent.be_notified and parent_email != self.author.email:
                email_list.append(parent_email)

            children = self.parent.children
            for child in children.all():
                child_email = child.author.email
                if child.be_notified and child_email != self.author.email:
                    email_list.append(child_email)
        return list(set(email_list))
