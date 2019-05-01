from django.contrib.auth import get_user_model, authenticate
# Translation import
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

# Django REST Framework Model serializer documentation
# https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
class UserSerializer(serializers.ModelSerializer):
    # Serializer for the Users object

    class Meta:
        model = get_user_model()
        # Fields that you want to include in the serializer.
        # Fields will be converted to and from JSON when we make our
        # HTTP Post and we retrieve that and our view.
        fields = ('email', 'password', 'name')
        # extra keyword args allows us to configure a few extra settings
        # in our model serializer.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        # Create a new user with encrypted password and return it
        return get_user_model().objects.create_user(**validated_data)

        ''' What Django REST Framework does is when we're ready
            to create user it will call the create function and pass
            in the validated_data. The validated_data will contain all
            of the data passed into our serializer which would be the
            JSON data as the argument.
        '''


class AuthTokenSerializer(serializers.Serializer):
    # Serializer for the user authentication objects
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
        # By default Django REST framework serializer will trim off white space
    )

    # Whenever you override the validate function you must return the
    # attrs at the end once validation is successful.
    def validate(self, attrs):
        # Validate and authenticate the user
        email = attrs.get('email')
        password = attrs.get('password')

        # When a request is made, it passes the context into the serializer
        # and from that we can get a hold of the request.
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials!')
            # Django REST framework passes the error as a 400 response, and
            # msg is sent to user.
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
