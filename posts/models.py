from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    image = models.ImageField(upload_to='posts/', null=True, blank=True)  # Add image field
    caption = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Post_{self.id}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by '{self.author}' on '{self.post}'"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post', 'comment')  # A user can like a post or comment only once.

    def __str__(self):
        if self.post:
            return f"Like by '{self.user}' on '{self.post}'"
        return f"Like by '{self.user}' on 'Comment_{self.comment.id}'"
