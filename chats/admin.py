from django.contrib import admin
from .models import Message, ChatGroup, ChatMessage


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'is_read']
    search_fields = ['sender__username', 'receiver__username']


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['members']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'group', 'created_at']
    search_fields = ['sender__username', 'group__name']
