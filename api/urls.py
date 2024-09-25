# urls.py
from django.urls import path,include
from .views import BookListView, BookDetailView, CategoryDetailView, CategoryListView, UserRegistrationView, LoginView, LogoutView, BookCreateView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'), 
    path('logout/', LogoutView.as_view(), name='user-logout'), 
    path('books/create/', BookCreateView.as_view(), name='book-create'),
 

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)