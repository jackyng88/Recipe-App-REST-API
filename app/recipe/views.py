from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers



class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    # Base viewset for user owned recipe attributes.
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Return objects for the current authenticated user only
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        # Create a new object
        # The perform_create function allows us to hook into the create
        # process when creating an object.
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    # Manage tags in the database
    # When you are defining a ListModelMixin and the GenericViewSet
    # you need to provide the queryset that you want to return.
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    # Manage ingredients in the database
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    # Manage recipes in the database
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Retrieve the recipes for the authentiated user
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        # Return appropriate serializer class.
        # Note: Overriding the get_serializer_class function. In the Django
        # REST framework documentation, get_serializer_class is the
        # function that is called to retrieve the serializer_class
        # for a given particular class.

        # self.action class variable will contain the action that is being
        # used for our current request.
        # if self.action is 'retrieve' it returns RecipeDetailSerializer
        # otherwise this returns RecipeSerializer
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new recipe
        serializer.save(user=self.request.user)
