from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class StatusChoices(models.TextChoices):
    """
    Choices for the status of posts and comments.
    """
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'


class ReactionChoices(models.TextChoices):
    """
    Choices for the type of reaction to a post or comment.
    """
    LIKE = 'like', 'Like'
    DISLIKE = 'dislike', 'Dislike'


class Post(models.Model):
    """
    Represents a post made by a user.
    """
    image = models.ImageField(upload_to='posts/')
    caption = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Post_{self.id}'


class Comment(models.Model):
    """
    Represents a comment on a post.

    A comment can be a direct comment or a reply to another comment.
    """
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name="replies", null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.parent:
            return f"Reply by '{self.author}' to comment {self.parent.id}"
        return f"Comment by '{self.author}' on '{self.post}'"


class Reaction(models.Model):
    """
    Represents a reaction (like or dislike) to a post or comment.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions", null=True, blank=True)
    reaction_type = models.CharField(max_length=10, choices=ReactionChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post', 'comment')  # Each user can react only once to a post or comment.

    def __str__(self):
        target = self.post if self.post else self.comment
        return f"{self.reaction_type.capitalize()} by '{self.user}' on '{target}'"


class Tag(models.Model):
    """
    Tags are used to categorize or label posts. A post can have multiple tags.
    """
    name = models.CharField(max_length=50, unique=True)
    posts = models.ManyToManyField(Post, related_name="tags")

    def __str__(self):
        return self.name
