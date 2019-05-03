from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')
# /api/recipe/recipes  What the RECIPES_URL might look like


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
