from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from utils.online_user_manager import OnlineUserManager
from accounts.serializers import UserListSerializer
from utils import custom_permissions
from .models import Chat, Message
from .serializers import ChatSerializer, ChatEditSerializer, MessageSerializer

User = get_user_model()


class ChatCreateView(generics.CreateAPIView):
    """
    View to create a new chat, either private or group.

    The view checks if the chat type is 'private' or 'group'.
    For private chats, checks if a chat with the other user already exists.
    For group chats, it requires a group name and a list of members.
    """
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        chat_type = request.data.get('type', '')

        # For private chats
        if chat_type == 'private':
            other_user_id = request.data.get('user_id')

            # Check if chat exists
            existing_chat = Chat.objects.filter(
                is_group=False,
                members=request.user
            ).filter(
                members__id=other_user_id
            ).first()

            if existing_chat:
                return Response({
                    'chat_id': existing_chat.id,
                    'message': 'private chat already exists!'
                })

            # Create new private chat
            chat = Chat.objects.create(is_group=False)
            chat.members.add(request.user, get_object_or_404(User, id=other_user_id))

            return Response({
                'chat_id': chat.id,
                'message': 'Private chat created'
            }, status=status.HTTP_201_CREATED)

        # For group chats
        elif chat_type == 'group':
            group_name = request.data.get('group_name')
            member_ids = request.data.get('members', [])

            if not group_name:
                return Response({
                    'group_name': 'Set Name For Group.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not member_ids:
                return Response({
                    'members': 'Set Group Members.'
                }, status=status.HTTP_400_BAD_REQUEST)

            chat = Chat.objects.create(
                name=group_name,
                is_group=True
            )

            # Add members
            members = [request.user] + list(User.objects.filter(id__in=member_ids))
            chat.members.add(*members)

            return Response({
                'chat_id': chat.id,
                'message': 'Group chat created'
            }, status=status.HTTP_201_CREATED)

        return Response({
            'type': 'Invalid chat type (private/group)'
        }, status=status.HTTP_400_BAD_REQUEST)


class ChatListView(generics.ListAPIView):
    """
    View to list all chats of the authenticated user.

    Returns a list of chats where the user is a member.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(members=self.request.user)


class ChatDetailView(generics.RetrieveAPIView):
    """
    View to retrieve the details of a specific chat.

    Returns chat details (e.g., name, type, members) for the chat that the user is a part of.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(members=self.request.user)


class ChatEditView(generics.UpdateAPIView):
    """
    View to edit chat details, manage members, and delete chats.

    Supports:
    - Adding new members
    - Removing members
    - Updating chat name or other details
    - Deleting the chat
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatEditSerializer

    def get_queryset(self):
        # Ensure user can only edit chats they are a member of
        return Chat.objects.filter(members=self.request.user)

    def perform_destroy(self, instance):
        # Custom delete method to ensure only chat members can delete
        if self.request.user not in instance.members.all():
            raise PermissionDenied({
                'message': 'You are not authorized to delete this chat.'
            })
        instance.delete()


class ChatMessagesView(generics.ListAPIView):
    """
    View to list all messages for a specific chat.

    Returns a list of messages for the specified chat, where the user has permission to view.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated,
                          custom_permissions.IsChatMemberPermission
                          ]

    def get_queryset(self):
        """
        Retrieves the messages for the chat specified by the chat_id in the URL.
        The user must be a member of the chat to view the messages.
        """
        user_id = self.request.user.id
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)

        if not chat.members.filter(id=user_id).exists():
            raise PermissionDenied({
                'message': 'You have not permission to view this chat.'
            })

        return Message.objects.filter(
            chat_id=chat_id
        ).order_by('created_at')


class OnlineUsersView(generics.ListAPIView):
    """
    View to list all online users.

    Returns a list of users who are currently online based on the cache.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the users that are currently online from the cache.
        """
        online_user_ids = OnlineUserManager.get_online_users()
        return User.objects.filter(id__in=online_user_ids)

    def list(self, request, *args, **kwargs):
        """
        Overridden to return a custom response with the list of online users and the count.
        """
        queryset = self.get_queryset()
        serializer = UserListSerializer(
            queryset=queryset,
            many=True,
            context={
                'request': request
            }
        )

        return Response({
            'online_users': serializer.data,
            'count': queryset.count()
        })
