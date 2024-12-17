from django.core.exceptions import ObjectDoesNotExist
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from asgiref.sync import sync_to_async

from utils.online_user_manager import OnlineUserManager
from chats.models import Chat, Message

import json


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat messages.

    This consumer manages WebSocket connections for individual chat rooms.
    It handles user authentication, chat membership verification, message broadcasting,
    and chat message saving to the database.
    """

    async def connect(self):
        """
        Handles the WebSocket connection to a specific chat room.

        Verifies user authentication with JWT token, checks if the chat exists, and if the user
        has permission to join. If all checks pass, the user is added to the group
        and the WebSocket connection is accepted.
        """
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_name = f'chat_{self.chat_id}'
        user = self.scope['user']

        # If user is not logged in, reject the connection
        if not user or not user.is_authenticated:
            raise DenyConnection("Invalid JWT Token")

        # Check if chat exists
        chat = await self.get_chat(self.chat_id)

        # Check if user have permission to join chat
        if not await self.is_user_in_chat(chat):
            raise DenyConnection("You are not a member of this chat")

        # Add the user to the chat group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def get_chat(self, chat_id):
        """
        Retrieves a chat by its ID.
        """
        try:
            return await database_sync_to_async(Chat.objects.get)(id=chat_id)
        except ObjectDoesNotExist:
            raise DenyConnection("Chat not found")

    async def is_user_in_chat(self, chat):
        """
        Checks if the authenticated user is a member of the given chat.
        """
        return await database_sync_to_async(
            chat.members.filter(
                id=self.scope['user'].id
            ).exists)()

    async def disconnect(self, close_code):
        # Remove the user from the chat group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handles receiving a message from the WebSocket, saves it to the database,
        and broadcasts it to other users in the chat room.
        """
        data = json.loads(text_data)
        message_content = data['message']
        user = self.scope['user']

        # Save the message to the database
        chat = await self.get_chat(self.chat_id)
        await database_sync_to_async(Message.objects.create)(
            chat=chat,
            sender=user,
            content=message_content
        )

        # Broadcast the message to all users in the chat room
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'username': user.username,
                'user_id': user.id,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))


class UserStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for managing user online/offline status.

    This WebSocket consumer manages users' online/offline status.
    When a user connects, they are marked as online and added to the "online_users" group.
    Upon disconnection, the user is marked as offline and removed from the group.
    """

    async def connect(self):
        """
        Handles the WebSocket connection for a user.

        Verifies user authentication with JWT token, marks the user as online, and adds the user
        to the "online_users" group to indicate their active status.
        """
        user = self.scope["user"]

        # Reject connection if user is not authenticated
        if not user or not user.is_authenticated:
            raise DenyConnection("Invalid JWT Token")

        # Mark user as online
        await sync_to_async(
            OnlineUserManager.mark_user_online
        )(user.id)

        # Add the user to the 'online_users' group to track their status
        await self.channel_layer.group_add(
            "online_users",
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]

        # Check if the user is authenticated before marking them offline
        if user or user.is_authenticated:
            # Mark user as offline
            await sync_to_async(
                OnlineUserManager.mark_user_offline
            )(user.id)

            # Remove user from online_users group
            await self.channel_layer.group_discard(
                "online_users",
                self.channel_name
            )
