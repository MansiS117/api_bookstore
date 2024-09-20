# urls.py
from django.urls import path
from .views import BookListView, BookDetailView, CategoryDetailView

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]
