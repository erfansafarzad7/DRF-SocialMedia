from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of a post to edit or delete it.

    This permission checks if the user making the request is the author of the post.
    - For read-only methods (GET, HEAD, OPTIONS), the permission is always granted.
    - For modifying methods (PUT, PATCH, DELETE), only the author of the post is allowed to proceed.
    """

    def has_object_permission(self, request, view, obj):
        # If the request is a read-only method, allow access
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow the author of the post to edit or delete it
        return obj.author == request.user
