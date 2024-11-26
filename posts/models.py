from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class StatusChoices:
    DRAFT = 0
    PUBLISHED = 1

    CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    ]


class Post(models.Model):
    image = models.ImageField(upload_to='posts/')
    caption = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    status = models.IntegerField(choices=StatusChoices.CHOICES, default=StatusChoices.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Post_{self.id}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    status = models.IntegerField(choices=StatusChoices.CHOICES, default=StatusChoices.DRAFT)
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

    def save(self, *args, **kwargs):
        if not (self.post or self.comment):
            raise ValueError("A like must be associated with either a post or a comment.")
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    posts = models.ManyToManyField(Post, related_name="tags")

    def __str__(self):
        return self.name
