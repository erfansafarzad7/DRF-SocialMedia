"""
ASGI config for social_media_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_project.settings')
django.setup()

from chats.routing import websocket_urlpatterns
from utils.jwt_auth_middleware import JWTAuthMiddleware


application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    # Custom Authentication
    "websocket": JWTAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
