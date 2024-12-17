from rest_framework import serializers
from .models import Chat, Message
from django.contrib.auth import get_user_model

User = get_user_model()


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


class ChatEditSerializer(serializers.ModelSerializer):
    """
    Serializer for editing chat details and managing members.
    """
    add_members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        required=False
    )
    remove_members = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        write_only=True,
        required=False
    )

    class Meta:
        model = Chat
        fields = ['name', 'is_group', 'add_members', 'remove_members']
        extra_kwargs = {
            'name': {'required': False},
            'is_group': {'required': False}
        }

    def update(self, instance, validated_data):
        # Handle adding members
        if 'add_members' in validated_data:
            for user in validated_data.pop('add_members'):
                instance.members.add(user)

        # Handle removing members
        if 'remove_members' in validated_data:
            for user in validated_data.pop('remove_members'):
                instance.members.remove(user)

        # Update chat details if provided
        if 'group_name' in validated_data:
            instance.name = validated_data['group_name']
        # if 'is_group' in validated_data:
        #     instance.is_group = validated_data['is_group']

        instance.save()
        return instance

    def validate(self, data):
        # Ensure the user making the request is a member of the chat
        user = self.context['request'].user
        chat = self.instance

        if user not in chat.members.all():
            raise serializers.ValidationError("You are not a member of this chat.")

        # Additional validations can be added here
        return data


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
