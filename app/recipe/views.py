from rest_framework.decorators import action
# the action decorator is what you use to add custom actions to your viewset.
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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
        '''
        Note
        Our assigned_only value will be a 0 or a 1. In the query_params
        there is no concept of 'type'. If 1 is the param, theres no way
        to know if it was a string or an int because they don't have quotes
        around them. So we first convert to int, then to boolean. This is
        because if we do bool() on a string with 0 in it then that will
        convert to true and assigned_only evaluates to true even if it
        was originally a 0.
        '''
        assigned_only = bool(
            # 0 is passed in as a default value for assigned_only if
            # not provided.
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

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

    def _params_to_ints(self, qs):
        # _ before function is python convention for a private function
        # Convert a list of string IDs to a list of integers
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        # Retrieve the recipes for the authentiated user
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            # Double underscure (__) is the Django syntax for filtering
            # on foreign key objects. We have a tags field in our
            # recipe queryset and that has a foreign key to our tags table
            # Another __ before a function 'in' which says to return
            # all of the tags where the id is in this list provided.
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        # Since we applied new parameters to our queryset it was changed
        # and reassigned to the variable 'queryset' so we no longer return
        # self.queryset but just return queryset
        return queryset.filter(user=self.request.user)

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
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new recipe
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        # Upload an image to a recipe
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            # these errors are automatically generated by the Django REST
            # framework. Auto-validation is performed on our field and if it
            # doesn't pass, errors is created.
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
