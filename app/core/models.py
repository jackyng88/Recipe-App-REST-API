from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings
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


class Tag(models.Model):
    # Tag to be used for a recipe
    name = models.CharField(max_length=255)
    # Instead of referencing the user model directly, we will use the best practice
    # of retrieving AUTH_USER_MODEL setting from Django settings
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    # Ingredients to be used in a recipe.
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    # Recipe object
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    # Django ManyToManyField documentation -
    # https://docs.djangoproject.com/en/2.1/ref/models/fields/#django.db.models.ManyToManyField
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.title
