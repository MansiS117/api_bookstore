# tests.py
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .models import User
from .serializer import UserRegistrationSerializer
from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from django.urls import reverse
from .models import User, Book, Cart, CartItem, Order, Category
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework import status
from .views import CartListView, CheckoutView
from api.factories import (
    UserFactory,
    OrderFactory,
    CategoryFactory,
    BookFactory,
)


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


class OrderViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.order = OrderFactory.create(buyer=self.user)

    def test_order_retrieve_view(self):
        """
        Test: Authorized user retrieving their own order.
        """
        url = reverse("order_confirmation", kwargs={"order_id": self.order.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data[''], self.order.user.email)
        self.assertEqual(response.data["buyer"], self.user.email)

    def test_order_retrieve_view_unauthorized(self):
        """
        Test: Unauthorized user trying to access an order.
        """
        other_user = UserFactory.create()

        self.client.force_authenticate(user=other_user)

        url = reverse("order_confirmation", kwargs={"order_id": self.order.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_retrieve_view_non_existent_order(self):
        """
        Test: Try to retrieve a non-existent order.
        """

        url = reverse("order_confirmation", kwargs={"order_id": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderListViewTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory.create()
        self.other_user = UserFactory.create()
        self.order1 = OrderFactory.create(buyer=self.user)
        self.order2 = OrderFactory.create(buyer=self.user)
        self.order3 = OrderFactory.create(buyer=self.other_user)
        self.client = APIClient()

    def test_order_list_view_authorized(self):

        self.client.force_authenticate(user=self.user)
        url = reverse("order_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_order_list_view_unauthorized(self):

        url = reverse("order_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_list_view_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("order_list")
        response = self.client.get(url)

        self.assertEqual(len(response.data), 1)

    def test_order_list_view_no_orders(self):
        user_no_orders = UserFactory.create()
        self.client.force_authenticate(user=user_no_orders)
        url = reverse("order_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_order_list_view_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("order_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order = response.data[0]
        self.assertIn("buyer", order)
        self.assertIn("total_price", order)
        self.assertIn("ordered_at", order)
        self.assertEqual(order["buyer"], self.user.email)
        self.assertEqual(
            float(order["total_price"]), float(self.order1.total_price)
        )


class CategoryViewTests(APITestCase):

    def setUp(self):
        """
        Set up initial test data using Factory Boy to create categories and books.
        """

        self.category1 = CategoryFactory()
        self.category2 = CategoryFactory()

        self.book1 = BookFactory(category=self.category1)
        self.book2 = BookFactory(category=self.category2)

        self.url = reverse("category-list")

        self.category_detail_url_1 = reverse(
            "category-detail", args=[self.category1.id]
        )
        self.category_detail_url_2 = reverse(
            "category-detail", args=[self.category1.id]
        )

    def test_category_list_view(self):
        """
        Test the CategoryListView to ensure it lists categories with the correct fields.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response data contains categories with only 'name' field
        self.assertEqual(
            len(response.data), 2
        )  # We expect 2 categories to be returned
        self.assertIn(
            "name", response.data[0]
        )  # Check if 'name' field is present in the first category
        self.assertIn(
            "name", response.data[1]
        )  # Check if 'name' field is present in the second category

        # Check the category names
        self.assertEqual(response.data[0]["name"], self.category1.name)
        self.assertEqual(response.data[1]["name"], self.category2.name)

    def test_category_list_view_empty(self):
        """
        Test the CategoryListView when there are no categories in the database.
        """

        Category.objects.all().delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_category_detail_view(self):
        """
        Test the CategoryDetailView to ensure it retrieves category details and books.
        """

        response = self.client.get(self.category_detail_url_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the 'name' and 'books' fields are present in the response
        self.assertIn("name", response.data)
        self.assertIn("books", response.data)

        # Check if the 'books' field contains the correct books
        self.assertEqual(len(response.data["books"]), 1)
        self.assertEqual(response.data["books"][0]["title"], self.book1.title)
