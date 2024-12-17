from rest_framework import serializers
from .models import Chat, Message


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for representing chat details, including group or private chat information,
    last message, and the count of members in the chat.
    """
    last_message = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'name', 'is_group', 'created_at', 'last_message', 'members_count']

    def get_last_message(self, obj):
        """
        Retrieves the last message in the chat.
        """
        last_msg = obj.messages.order_by('-created_at').first()
        return {
            'content': last_msg.content if last_msg else None,
            'sender': last_msg.sender.username if last_msg else None,
            'created_at': last_msg.created_at if last_msg else None
        }

    def get_members_count(self, obj):
        return obj.members.count()


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for representing message details,
    including the sender's username and message content.
    """
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'content', 'sender', 'sender_username', 'created_at']
        read_only_fields = ['sender', 'created_at']
