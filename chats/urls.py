from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, ChatGroupViewSet, ChatMessageViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet)
router.register(r'chat_groups', ChatGroupViewSet)
router.register(r'chat_messages', ChatMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
