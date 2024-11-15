from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from .models import Post, Comment, Like, Tag
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, TagSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post_id = self.request.data.get("post")
        serializer.save(author=self.request.user, post_id=post_id)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.request.data.get("post")
        comment_id = self.request.data.get("comment")

        if post_id and comment_id:
            raise ValidationError("A like can be associated with either a post or a comment, not both.")

        if Like.objects.filter(user=self.request.user, post_id=post_id, comment_id=comment_id).exists():
            raise ValidationError("You have already liked this post or comment.")

        serializer.save(user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
