from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .models import StatusChoices, Post, Comment, Like, Tag
from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer, LikeSerializer, TagSerializer
from utils.permissions import IsAuthorOrReadOnly
from .filters import PostFilter


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PostFilter  # Connect the filter
    # search_fields = ['caption', 'tags__name']  # Optional search fields

    def get_serializer_class(self):
        # if self.action == 'list':
        #     return PostListSerializer
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer  # Fallback or for other actions like create/update

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    # queryset = Comment.objects.filter(status=1).order_by('-created_at')
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Override the default queryset to filter only published comments.
        """
        queryset = Comment.objects.filter(status=StatusChoices.PUBLISHED)
        return queryset.order_by('-created_at')

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
