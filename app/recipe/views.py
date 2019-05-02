from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient

from recipe import serializers



class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    # Manage tags in the database
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # When you are defining a ListModelMixin and the GenericViewSet
    # you need to provide the queryset that you want to return.
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # overriding the get_queryset function
    def get_queryset(self):
        # Return objects for the current authenticated user only
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        # Create a new tag.
        # The perform_create function allows us to hook into the create
        # process when creating an object.
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    # Manage ingredients in the database
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        # Return objects for the curent authenticated user
        return self.queryset.filter(user=self.request.user).order_by('-name')
