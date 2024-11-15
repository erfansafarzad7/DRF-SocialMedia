from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, ChatGroup, ChatMessage


User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'created_at', 'is_read']


class ChatGroupSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = ChatGroup
        fields = ['id', 'name', 'members', 'created_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=ChatGroup.objects.all())

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'group', 'content', 'created_at']
