from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Book, Category, User, USER_TYPE_CHOICES, Cart, CartItem


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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Authenticate the user
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid login credentials.")

        attrs["user"] = (
            user  # Add the authenticated user to the validated data
        )
        return attrs


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("title", "image", "price", "author")


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name",)


class CategoryDetailSerializer(serializers.ModelSerializer):
    books = BookListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("name", "books")  # or specify fields explicitly


class BookDetailSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    seller = UserSerializer(read_only=True)

    class Meta:
        model = Book
        fields = (
            "title",
            "author",
            "image",
            "seller",
            "description",
            "price",
            "is_available",
            "category",
        )  # or specify fields explicitly

    def create(self, validated_data):
        # Get the category name from the original input data
        category_name = self.initial_data.get("category", None)

        if category_name:
            # Get or create the category instance
            category, created = Category.objects.get_or_create(
                name=category_name
            )
            validated_data["category"] = (
                category  # Assign the category instance to validated_data
            )

        return super().create(validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    book = serializers.CharField()

    class Meta:
        model = CartItem
        fields = ("book", "quantity")

    def update(self, instance, validated_data):
        book_title = validated_data.pop("book", None)
        if book_title:
            try:
                book_instance = Book.objects.get(title__icontains=book_title)
                instance.book = book_instance
            except Book.DoesNotExist:
                raise serializers.ValidationError(
                    {"book": "Book does not exist."}
                )

        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ("buyer", "items")

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        # Extract the items data
        buyer = validated_data["buyer"]

        cart, created = Cart.objects.get_or_create(
            **validated_data
        )  # Create the cart instance

        # Now create CartItem instances for each item
        for item_data in items_data:
            book_title = item_data.pop("book")  # Extract book title
            try:
                book_instance = Book.objects.get(
                    title__icontains=book_title
                )  # Look up the book by title
            except Book.DoesNotExist:
                raise serializers.ValidationError(
                    {"book": f"Book '{book_title}' does not exist."}
                )

            # Create CartItem and associate it with the newly created cart
            CartItem.objects.create(cart=cart, book=book_instance, **item_data)

        return cart
