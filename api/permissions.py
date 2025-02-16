from rest_framework import permissions

class IsSeller(permissions.BasePermission):
    """
    Custom permission to only allow sellers to modify books.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'seller'

class IsBuyer(permissions.BasePermission):
    """
    Custom permission to only allow buyers to access cart endpoints.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'buyer'


class CanRetrieveOrIsSeller(permissions.BasePermission):
    """
    Custom permission that allows all authenticated users to retrieve books,
    but only allows the seller who owns the book to update or delete it.
    """

    def has_permission(self, request, view):
        # Allow read access to all authenticated users
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read access to all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow the seller to update or delete their own book
        return obj.seller == request.user
    