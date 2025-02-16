import factory
from api.models import User, Order, Category, Book


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    user_type = "buyer"
    password = factory.PostGenerationMethodCall("set_password", "password123")


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    total_price = factory.Faker("random_number", digits=5)
    buyer = factory.SubFactory(UserFactory)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("word")


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Faker("sentence")
    category = factory.SubFactory(CategoryFactory)
    price = factory.Faker(
        "random_number", digits=2
    )  # Generate a random number for the price (e.g., 10, 25, etc.)
    seller = factory.SubFactory(UserFactory, user_type="seller")
