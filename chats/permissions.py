from rest_framework import permissions
from django.shortcuts import get_object_or_404
from chats.models import Chat


class IsChatMemberPermission(permissions.BasePermission):
    """
    This permission ensures that only users who are members of the chat, can access the chat.
    """

    def has_permission(self, request, view):
        user_id = request.user.id
        chat_id = view.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)  # Retrieve the chat object

        if chat:
            # Check if the user is a member of the chat
            return chat.members.filter(id=user_id).exists()

        return False
