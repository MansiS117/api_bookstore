# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from .views import (
    BookCreateView,
    BookDetailView,
    BookListView,
    CategoryDetailView,
    CategoryListView,
    LoginView,
    LogoutView,
    UserRegistrationView,
    CartListView,
    CartUpdateDeleteView,
)

urlpatterns = [
    path("books/", BookListView.as_view(), name="book-list"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<int:pk>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    path("books/create/", BookCreateView.as_view(), name="book-create"),
    path("cart/", CartListView.as_view(), name="cart"),
    path("cart/<int:pk>/", CartUpdateDeleteView.as_view(), name="cart-update"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
