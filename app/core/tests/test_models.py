# tests that our helper function for our model can create a new user.
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@test.com', password='testpass'):
    # Create a sample user
    return get_user_model().objects.create_user(email,password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        # test creating a new user with an email is successful.
        email = 'test@test.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test whether the email for a new user is normalized.
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_usr_invalid_email(self):
        # Test creating user with no email raises error.
        with self.assertRaises(ValueError):
            # if this doesn't run a ValueError, then test will fail.
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        # Test creating a new superuser.
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123'
        )

        # is_superuser function we didn't create but is included in PermissionsMixin.
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        # Test the tag string representation
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        # Test the ingredient string representation
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        # Test the recipe string representation
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='General Tso\'s Chicken',
            time_minutes=5,
            price=5.00
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        # Test that image is saved in the correct location.
        # We're going to mock the uuid function from the default
        # uuid library that comes with Python.
        uuid = 'test-uuid'
        # any time we call the uuid4 function that is triggered from
        # within the test, it will change the value and override the
        # default behavior and just return 'test-uuid' instead.
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        # f'' is an fstring or 'literal string interpolation'. Which allows
        # us to insert our variables inside our string without having to
        # use the variable dot format by surrounding them with {}.
        expected_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)
