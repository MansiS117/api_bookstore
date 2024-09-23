# urls.py
from django.urls import path,include
from .views import BookListView, BookDetailView, CategoryDetailView, CategoryListView, UserRegistrationView



urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
]

