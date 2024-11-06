from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .models import User
from .serializer import UserRegistrationSerializer

# tests.py
from rest_framework.test import APITestCase, APIRequestFactory
from django.urls import reverse
from .models import User, Book, Cart, CartItem, Order
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework import status
from .views import CartListView, CheckoutView


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


class LoginViewTest(APITestCase):
    def setUp(self):
        # Create a test user with email and password
        self.email = "testuser@example.com"
        self.password = "strong_password"
        self.user = User.objects.create_user(
            email=self.email, password=self.password
        )  # Use email only
        self.url = reverse(
            "user-login"
        )  # Ensure the URL name matches your URL configuration

    def test_login_success(self):
        # Define the payload for a successful login
        payload = {
            "email": self.email,  # Use email for login
            "password": self.password,
        }

        # Make a POST request to the login view
        response = self.client.post(self.url, payload, format="json")

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "token", response.data
        )  # Check if the token is in the response
        self.assertEqual(response.data["message"], "Logged in successfully.")

        # Verify that a token has been created for the user
        token = Token.objects.get(user=self.user)
        self.assertIsNotNone(token)

    def test_login_invalid_credentials(self):
        # Define the payload for an unsuccessful login
        payload = {
            "email": self.email,  # Use email for login
            "password": "wrong_password",  # Incorrect password
        }

        # Make a POST request to the login view
        response = self.client.post(self.url, payload, format="json")

        # Assert that the response indicates a bad request
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "non_field_errors", response.data
        )  # Check for error in response


class BookCreateViewTest(APITestCase):
    def setUp(self):
        self.seller_user = User.objects.create_user(
            email="seller@example.com", password="testpass", user_type="seller"
        )
        self.seller_user.is_active = True
        self.seller_user.save()

        self.url = reverse("book-create")

    def test_create_book(self):
        self.client.force_authenticate(user=self.seller_user)

        data = {
            "title": "Test Book",
            "author": "Test Author",
            "price": 100,
            "description": "A book for testing purposes",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.get().title, "Test Book")

    def test_create_book_unauthenticated(self):
        data = {
            "title": "Another Test Book",
            "author": "Test Author",
            "price": 12.99,
            "description": "A book for testing purposes.",
        }
        response = self.client.post(self.url, data, format="json")
        # Assert that the response status code is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CartListViewTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.buyer_user = User.objects.create_user(
            email="buyer@example.com", password="testpass", user_type="buyer"
        )
        self.seller_user = User.objects.create_user(
            email="seller@example.com", password="testpass", user_type="seller"
        )
        self.cart = Cart.objects.create(buyer=self.buyer_user)

        # Create a Book instance and assign it to the seller
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            price=100,
            description="A book for testing purposes",
            seller=self.seller_user,  # Set the seller
        )

        # URL for the cart list endpoint
        self.url = reverse("cart")  # Adjusted to match your URL pattern name

    def test_create_cart_authenticated(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.buyer_user)

        # Data for creating a cart
        cart_data = {"items": [{"book": "Test Book", "quantity": 2}]}

        # Make the request with the client
        response = self.client.post(self.url, cart_data, format="json")

        # Check the response status

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CheckoutViewTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.buyer_user = User.objects.create_user(
            email="buyer@example.com", password="testpass", user_type="buyer"
        )

        # Create a cart for the buyer
        self.cart = Cart.objects.create(buyer=self.buyer_user)

        # Create a book and add it to the cart
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            price=100,
            description="A book for testing purposes",
            seller=self.buyer_user,  # Assuming the buyer is also a seller for this test
        )

        self.cart_item = CartItem.objects.create(
            cart=self.cart, book=self.book, quantity=2
        )

        self.url = reverse("checkout")  # Adjust to your actual URL pattern


class CheckoutViewTestCase(APITestCase):
    fixtures = [
        "api/fixtures/user_fixtures.json",
        "api/fixtures/book_fixtures.json",
    ]  # Only load the books fixture (since books are required for the test)

    def setUp(self):
        # Create the buyer and seller users programmatically
        self.user = User.objects.get(pk=1)
        self.seller = User.objects.get(pk=2)

        # Authenticate the buyer
        self.client.force_authenticate(user=self.user)

        # Create a cart for the user
        self.cart = Cart.objects.create(buyer=self.user)

        # Fetch books from the fixture
        book1 = Book.objects.get(pk=1)
        book2 = Book.objects.get(pk=2)

        # Add items to the cart
        CartItem.objects.create(cart=self.cart, book=book1, quantity=2)
        CartItem.objects.create(cart=self.cart, book=book2, quantity=1)

    def test_checkout_success(self):
        url = reverse("checkout")
        response = self.client.post(url)

        # Assert the order creation and response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["total_price"], 55.0
        )  # Assuming the total price is 55
        self.assertEqual(
            self.user.order_set.count(), 1
        )  # There should be 1 order created

        # Check that the cart is empty after checkout
        self.assertEqual(self.cart.items.count(), 0)
        self.assertFalse(
            Cart.objects.filter(id=self.cart.id).exists()
        )  # Cart should be deleted
