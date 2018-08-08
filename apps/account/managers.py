"""
This module allows to extend the default manager provided by Django models.
"""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """ Manager overriding the default Base User Manager because we save
        the user with the email instead of the username.
    """

    def create_user(self, email, first_name, password=None):
        """ Creates and saves a User with the given email and password. """
        if not email:
            raise ValueError('Email must be set.')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password):
        """ Creates and saves a superuser with the given email, password. """
        user = self.create_user(email, first_name, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
