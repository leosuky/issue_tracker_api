"""
Database Models
----------------------------------------------
This works because we update the AUTH_USER_MODEL
setting in our settings.py file.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Overriding the base User Manager"""

    def create_user(self, email, password=None, **kwargs):
        """Create, Save and Return New User"""
        if not email:
            raise ValueError('User must have an Email Address')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Overriding the default user model in django"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    """Assign manager to User Class"""
    objects = UserManager()

    USERNAME_FIELD = 'email'
