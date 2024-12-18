from rest_framework import permissions


class IsOwnProfile(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profile.
    """

    def has_object_permission(self, request, view, obj):
        # If the request is a read-only method, allow access
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow users to edit their own profile only
        if request.method in ['PUT', 'PATCH']:
            return obj == request.user

        return False
