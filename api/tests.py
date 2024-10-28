from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .models import User
from .serializer import UserRegistrationSerializer
# tests.py
from rest_framework.test import APITestCase
from django.urls import reverse
from .models  import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model 

# Create your tests here.
class UserRegistrationSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "strong_password",
            "confirm_password": "strong_password",
            "user_type": "buyer",
        }
    def test_user_registration_serializer_valid(self):
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.first_name, self.valid_data["first_name"])
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertTrue(user.check_password(self.valid_data["password"]))



# tests.py

User = get_user_model()  # Get the custom user model

class LoginViewTest(APITestCase):
    def setUp(self):
        # Create a test user with email and password
        self.email = 'testuser@example.com'
        self.password = 'strong_password'
        self.user = User.objects.create_user(email=self.email, password=self.password)  # Use email only
        self.url = reverse('user-login')  # Ensure the URL name matches your URL configuration

    def test_login_success(self):
        # Define the payload for a successful login
        payload = {
            'email': self.email,  # Use email for login
            'password': self.password,
        }

        # Make a POST request to the login view
        response = self.client.post(self.url, payload, format='json')

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)  # Check if the token is in the response
        self.assertEqual(response.data['message'], "Logged in successfully.")

        # Verify that a token has been created for the user
        token = Token.objects.get(user=self.user)
        self.assertIsNotNone(token)

    def test_login_invalid_credentials(self):
        # Define the payload for an unsuccessful login
        payload = {
            'email': self.email,  # Use email for login
            'password': 'wrong_password',  # Incorrect password
        }

        # Make a POST request to the login view
        response = self.client.post(self.url, payload, format='json')

        # Assert that the response indicates a bad request
        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)  # Check for error in response
