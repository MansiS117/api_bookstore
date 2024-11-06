import factory
from api.models import User, Order


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
