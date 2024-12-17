from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Chat(models.Model):
    """
    Represents a chat room, which can either be a private chat or a group chat.
    """
    name = models.CharField(max_length=255, null=True, blank=True)  # For group chats, this can be the group name
    is_group = models.BooleanField(default=False)  # Whether the chat is a group chat or private chat
    members = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'"{self.name[:10]}" - {self.id}' if self.name else f'"private" - {self.id}'

    def get_last_message(self):
        """
        Retrieves the most recent message in the chat.
        """
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """
    Represents a message in a chat.
    """
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
