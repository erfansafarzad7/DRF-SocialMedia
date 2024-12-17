from django.contrib import admin
from .models import Chat, Message


def mark_as_read(modeladmin, request, queryset):
    """
    Marks selected messages as read.
    """
    queryset.update(is_read=True)
mark_as_read.short_description = "Mark selected messages as read"


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_group', 'created_at')
    list_filter = ('is_group', 'created_at')
    search_fields = ('id', 'name')
    ordering = ('-created_at',)
    filter_horizontal = ('members',)  # For many-to-many field 'members' to make selection easier


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'content', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'chat')
    search_fields = ('id', 'content', 'sender__username', 'chat__name')  # Searching by sender username and chat name
    ordering = ('-created_at',)
    actions = [mark_as_read]
