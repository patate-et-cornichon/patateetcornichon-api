import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from common.db.abstract_models import DatedModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, DatedModel):

    # Custom ID with an UUID instead of the default one
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # As there is no username in the auth model, the unique way to identify the user is with
    # his email.
    email = models.EmailField(max_length=100, unique=True)

    # Extra user information
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40, null=True, blank=True)
    avatar = models.FileField(upload_to='avatars/', null=True)
    website = models.URLField(max_length=255, null=True, blank=True)

    # User permission
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    def __str__(self):
        return self.email


class UnregisteredUser(models.Model):
    """ Represents an unregistered user. """

    # Custom ID with an UUID instead of the default one
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(max_length=150, unique=True, db_index=True)

    # Extra user information
    first_name = models.CharField(max_length=40)
    avatar = models.FileField(upload_to='avatars/', null=True)
    website = models.URLField(null=True)
