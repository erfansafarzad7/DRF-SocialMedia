from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of a post to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # If the request is a read-only method, allow access
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow the author of the post to edit or delete it
        return obj.author == request.user


class IsOwnProfile(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profile.
    and
    """

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, or OPTIONS requests (read-only)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Allow users to edit their own profile only
        if request.method in ['PUT', 'PATCH']:
            return obj == request.user

        return False
