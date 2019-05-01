from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

from recipe import serializers



class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
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
