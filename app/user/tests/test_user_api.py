from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# REST framework test helper tools
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)



class PublicUserApiTests(TestCase):
    # Test the Users API (public)

    def setUp(self):
        # Makes it easier to call client. We don't need to constantly
        # recreate the APIClient so we can reuse it.
        self.client = APIClient()

    def test_create_valid_user_success(self):
        # Test creating user with valid payload(object) is successful.
        payload = {
            'email': 'strawhat@grandline.com',
            'password': 'onepiece',
            'name': 'Monkey D. Luffy'
        }
        # This will do a HTTP POST request to our client to our URL.
        res = self.client.post(CREATE_USER_URL, payload)

        # Makes sure that our API returns HTTP 201 when object is created.
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Test that object is actually created.
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))

        # Check that password is not returned as part of the object.
        # We don't want it returned because it is a potential security risk.
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        # Test creating a user that already exists fails
        payload = {
            'email': 'strawhat@grandline.com',
            'password': 'onepiece',
        }
        # ** will unwind payload i.e. email and password
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        # We are expecting a HTTP 400 Bad request, because user exists.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        # Test that the password must be more than 5 characters.
        payload = {
            'email': 'strawhat@grandline.com',
            'password': 'pw'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # If user exists, this will return true.Otherwise returns false.
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    ''' Following tests are testing obtaining of tokens and authentication'''

    def test_create_token_for_user(self):
        # Test that a token is created for the user.
        payload = {'email': 'test@test.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_create_token_invalid_credentials(self):
        # Test that token is not created if invalid credentials are given
        create_user(email='test@test.com', password='testpass')
        payload = {'email': 'test@test.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        # Test that token is not created if user doesn't exist
        payload = {'email': 'test@test.com', 'password': 'testpass'}
        # Unlike above tests, we don't create user to test if a token is obtained.
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        # Test that email and password are required
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        # Test that authentication is required for users.
        res = self.client.get(ME_URL)

        # Makes sure if you call the URL without authentication it returns
        # HTTP_401_UNAUTHORIZED
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    # Test API requests that require authentication

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            password='testpass',
            name='name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        # Test retrieving profile for logged in user
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Test for retrieving profile
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        # Test that post is not allowed on the ME_URL
        res = self.client.post(ME_URL, {})

        # HTTP405 is the standard response when you do an HTTP Method
        # that is not allowed on the API.
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        # Test updating the user profile for authenticated user
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        # Updates user with the latest values from the database.
        self.user.refresh_from_db()

        # Tests for name being equal, and password exists
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.password, payload['password'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
