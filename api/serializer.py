from rest_framework import serializers
from .models import Book, Category, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name',) 

class CategorySerializer(serializers.ModelSerializer):
     class Meta:
        model = Category
        fields = ("name",)# or specify fields explicitly

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    seller = UserSerializer(read_only=True)
    class Meta:
        model = Book
        fields =  ("title", "author", "seller", "category", "price")  # or specify fields explicitly
