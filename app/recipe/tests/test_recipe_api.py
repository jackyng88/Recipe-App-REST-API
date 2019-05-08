import tempfile
import os

# PIL is the Pillow library.
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')
# /api/recipe/recipes  What the RECIPES_URL might look like


def image_upload_url(recipe_id):
    # Return URL for recipe image upload
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    # return recipe detail URL
    # /api/recipe/recipes/2/ The 2 might be what is passed into the recipe_id
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main Course'):
    # Create and return a sample tag
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Vanilla'):
    # Create and return a sample ingredient
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    # Create and return a sample recipe
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    # Python's update function accepts a dictionary object and will take
    # whichever keys are in the dictionary and update them. If they don't
    # exist, it will create them.
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    # Test unauthenticated API access

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test that authentication is required
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    # Test unauthenticated recipe API access

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        # Test retrieving a list of recipes
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        # Test retrieving recipes for user
        user2 = get_user_model().objects.create_user(
            'other@test.com',
            'password123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        # Test viewing a recipe detail
        recipe = sample_recipe(user=self.user)
        # .add is how you an item on a ManyToManyField
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        # Test creating recipe
        payload = {
            'title': 'Ddeokkbokki',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        # HTTP 201 is the standard HTTP code for creating objects in an API.
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # When you create an object in the Django REST framework the default
        # behavior is that it will return a dictionary containing the created
        # object. Thus res.data['id'] will retrieve the id of the object.
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            # looping through keys in the dictionary
            # getattr is a Python standard library function that allows you
            # to retrieve an attribute from an object by passing in a variable
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        # Test creating a recipe with tag
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Desert')
        payload = {
            'title': 'Key Lime Pie',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        # Due to the fact that we have a ManyToManyField assigned to our
        # tags (from models.py), this will return all of the tags that are
        # assigned to our recipe object as a queryset.
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        # Test creating recipe with ingredients
        ingredient1 = sample_ingredient(user=self.user, name='Abalone')
        ingredient2 = sample_ingredient(user=self.user, name='Garlic')
        payload = {
            'title': 'Feast of the Sea',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 30,
            'price': 50.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        # Test updating a recipe with 'patch'
        # 'patch' - is used to update the fields in a payload. It will only
        # change the fields that are provided. Ommitted ones will not change.
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {'title': 'Chicken Tikka', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        # both tags.count() and len(tags) work
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        # Test updating a recipe with 'put'
        # 'put'- will replace the full object that we're updating. If you
        # exclude any fields in the payload those fields will actually
        # be removed from the object that you're updating.
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Chicken Schwarma',
            'time_minutes': 20,
            'price': 6.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        # function to tear down and clear test files from our object.
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        # Test uploading an image to recipe
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # creates a temporary file on the system that we can then
            # write to and then after we exit the context manager (with)
            # it will automatically remove that file.
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            # The way that python reads files. Because we saved the file
            # the seeking would be at the end of the file and we would
            # just have a blank. We use seek(0) to set it to the beginning
            # of the file again.
            ntf.seek(0)
            # We need the multipart format because we need to tell Django
            # that we want to make a multipart form request which means a
            # a form that consists of data. By default it would be a form
            # that contains a JSON object.
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check that image is in the response and that the path is saved
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        # Test uploading an invalid image
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        # Test returning recipes with specific tags
        recipe1 = sample_recipe(user=self.user, title='Thai Veggie Curry')
        recipe2 = sample_recipe(user=self.user, title='Yummy Chicken')
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Meat')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(user=self.user, title='Fish and Chips')

        res = self.client.get(
            RECIPES_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        # Test returning recipes with specific ingredients
        recipe1 = sample_recipe(user=self.user, title='Sloppy Joe')
        recipe2 = sample_recipe(user=self.user, title='Double Cooked Pork')
        ingredient1 = sample_ingredient(user=self.user, name='Ground Beef')
        ingredient2 = sample_ingredient(user=self.user, name='Pork')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_recipe(user=self.user, title='T-Bone Steak')

        res = self.client.get(
            RECIPES_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
