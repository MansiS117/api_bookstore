from .serializer import BookSerializer, CategorySerializer, UserRegistrationSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Book, Category
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated



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
    

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']  # Get the authenticated user
            token, created = Token.objects.get_or_create(user=user)  # Create or retrieve token
            
            return Response({
                "token": str(token),
                "message": "Logged in successfully."
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        # Get the token for the authenticated user
        token = request.auth  # The token is available in the request

        if token is not None:
            # Delete the token to log out the user
            token.delete()

            return Response({
                "message": "Logged out successfully."
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "No active session found."
        }, status=status.HTTP_400_BAD_REQUEST)