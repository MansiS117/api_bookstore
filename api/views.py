from .serializer import (
    BookDetailSerializer,
    BookListSerializer,
    CategoryListSerializer,
    CategoryDetailSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderItemSerializer,
    OrderSerializer,
)
from rest_framework.response import Response
from rest_framework import generics, status, filters, mixins
from .models import Book, Category, Cart, CartItem, Order, OrderItem
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSeller, IsBuyer, CanRetrieveOrIsSeller
from .pagination import CustomPagination
from django.shortcuts import get_object_or_404


class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description", "category__name", "author"]
    pagination_class = CustomPagination


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = [CanRetrieveOrIsSeller]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Registration successful!",
                "user": {"email": user.email, "user_type": user.user_type},
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data[
                "user"
            ]  # Get the authenticated user
            token, created = Token.objects.get_or_create(
                user=user
            )  # Create or retrieve token

            return Response(
                {"token": str(token), "message": "Logged in successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        # Get the token for the authenticated user
        token = request.auth  # The token is available in the request

        if token is not None:
            # Delete the token to log out the user
            token.delete()

            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "No active session found."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class BookCreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = [IsSeller]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class CartListView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsBuyer]

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    def get_queryset(self):
        # Return only the carts belonging to the authenticated user
        return Cart.objects.filter(buyer=self.request.user)


class CartUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsBuyer]

    def get_queryset(self):
        # Return only the carts belonging to the authenticated user
        return CartItem.objects.filter(cart__buyer=self.request.user)


class CheckoutView(APIView):
    permission_classes = [IsBuyer]

    def post(self, request):
        cart = get_object_or_404(Cart, buyer=request.user)

        total_price = 0
        order_items = []

        for cart_item in cart.items.all():
            total_price += cart_item.book.price * cart_item.quantity
            order_items.append(
                {
                    "book": cart_item.book,
                    "quantity": cart_item.quantity,
                    "unit_price": cart_item.book.price,
                }
            )

        order = Order.objects.create(
            buyer=request.user, total_price=total_price
        )

        for item in order_items:
            OrderItem.objects.create(
                order=order,
                book=item["book"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )

        cart.items.all().delete()
        cart.delete()

        
        response_data = {
            "message": "Checkout successful!",
            "order_id": order.id,
            "total_price": total_price,
        }

        return Response(
            response_data, status=status.HTTP_201_CREATED
        )  # Directly returning response data


class OrderView(generics.RetrieveAPIView):
  
    serializer_class = OrderSerializer
    permission_classes = [IsBuyer]

    def get_object(self):
        order_id = self.kwargs.get(
            "order_id"
        )  # Since the order id is passed as order_id
        order = get_object_or_404(Order, id=order_id, buyer=self.request.user)
        return order
    
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsBuyer]
    def get_queryset(self):
         return Order.objects.filter(buyer=self.request.user)
