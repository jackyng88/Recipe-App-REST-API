from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


# Django REST Framework APIView documentation -
# https://www.django-rest-framework.org/api-guide/generic-views/#createapiview

# We will use the CreateAPIView that comes with the Django REST framework
class CreateUserView(generics.CreateAPIView):
    # Create a new user in the system
    # This view specificies a class variable that points to the Serializer class
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    # Create a new auth token for user
    serializer_class = AuthTokenSerializer
    # Set our renderer class. This allows us to view this endpoint
    # in the browser with the browsable API.
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    # Manage the authenticated user
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        # Retrieve and return authenticated user
        return self.request.user
        # When get_object is called the request will have the user attached
        # because of the authentication_classes. Takes care of getting the
        # authenticated user and assigning it to a request.
