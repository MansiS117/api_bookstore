from .serializer import BookSerializer, CategorySerializer, UserRegistrationSerializer
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Book, Category
from rest_framework import viewsets

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class CategoryListView(generics.ListAPIView):   
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()   
    serializer_class = CategorySerializer

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Registration successful!", 
            "user": {
                "email": user.email,
                "user_type": user.user_type
            }
        }, status=status.HTTP_201_CREATED)
    

