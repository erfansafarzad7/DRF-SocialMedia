from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

import os
import django
import jwt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_project.settings')
django.setup()

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    """
    Decodes the JWT token and retrieves the user associated with it.

    This function decodes the provided JWT token to extract the user ID from its payload.
    If the token is valid and the user exists, the corresponding user is returned.
    If the token is expired, invalid, or the user doesn't exist, it returns None.
    """
    try:
        # Decode JWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            return None
        return User.objects.get(id=user_id)

    # Return None if the token is invalid or the user doesn't exist
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate users based on JWT token.
    """

    async def __call__(self, scope, receive, send):
        """
        Processes the WebSocket connection request and adds the authenticated user to the scope.

        Extracts the JWT token from the 'Authorization' header, decodes it, and retrieves
        the user associated with the token. If the token is valid, the user is added to
        the scope, making it accessible to consumers.
        """
        headers = dict(scope["headers"])
        token = None

        # Check for 'Authorization' header
        if b"authorization" in headers:
            auth_header = headers[b"authorization"].decode()  # Decode the header
            if auth_header.startswith("Bearer "):  # Ensure it's Bearer token
                token = auth_header.split(" ")[1]

        # Add user to scope if token is valid
        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = None

        return await super().__call__(scope, receive, send)
