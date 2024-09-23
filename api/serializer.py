from rest_framework import serializers
from .models import Book, Category, User, USER_TYPE_CHOICES


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name",)


class UserRegistrationSerializer(serializers.ModelSerializer):
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES, default="buyer"
    )
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "user_type",
        )
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop(
            "confirm_password"
        )  # Remove confirm_password before creating the user
        user = User(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            user_type=validated_data.get(
                "user_type", "buyer"
            ),  # Default to 'buyer'
        )
        user.set_password(validated_data["password"])  # Hash the password
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name",)  # or specify fields explicitly


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    seller = UserSerializer(read_only=True)

    class Meta:
        model = Book
        fields = (
            "title",
            "author",
            "seller",
            "category",
            "price",
            "is_available",
        )  # or specify fields explicitly
