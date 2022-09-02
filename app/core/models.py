"""
Database Models
----------------------------------------------
This works because we update the AUTH_USER_MODEL
setting in our settings.py file.
"""
from django.conf import settings
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


class Project(models.Model):
    """Project Object"""
    PROJECT_STATUS = (
        ('Design', 'Design'),
        ('Implementation', 'Implementation'),
        ('Testing', 'Testing'),
        ('Deployment', 'Deployment'),
        ('Completed', 'Completed'),
        ('Abandoned', 'Abandoned'),
    )

    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )   # its best practice to reference the User model from settings.py
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=200, choices=PROJECT_STATUS, null=True, blank=True
    )
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
