from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
# these are all things needed to extend Django user model.


class UserManager(BaseUserManager):

    # what **extra_fields does is, takes all the extra functions passed in and
    # passed them into the extra fields.
    def create_user(self, email, password = None, **extra_fields):
        # Creates and saves a new user.
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email = self.normalize_email(email), **extra_fields)
        # password can't be set in above call because it must be encrypted.
        user.set_password(password)
        # this is required for supporting multiple databases.
        user.save(using = self._db)

        return user

    def create_superuser(self, email, password):
        # Creates and saves a new super user.
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Custom user models that supports using email instead of username.
    email = models.EmailField(max_length = 255, unique = True)
    name = models.CharField(max_length = 255)
    # is_active allows if a user is active or not. Allows to deactivate.
    is_active = models.BooleanField(default = True)
    # users are active by default, but not staff.
    is_staff = models.BooleanField(default = False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
