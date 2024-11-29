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
