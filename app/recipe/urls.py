from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views

'''
The DefaultRouter is a feature of the Django REST framework that will
automatically generate the URLs for our viewset. When you have a viewset
you may have multiple have multiple URLs associated with that one viewset.

examples -
/api/recipe/tags
/api/recipe/tags/1/

The DefaultRouter automatically registers the appropriate URLs for all
of the actions in our viewset.
'''

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
