from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import notify_followers
from .permissions import IsAuthorOrReadOnly
from .filters import PostFilter
from .models import StatusChoices, Post, Comment, Tag
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    ReactionSerializer,
    TagSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and deleting posts.

    - The viewset filters posts to only show published ones.
    - It provides different serializers for different actions:
        - `PostListSerializer` for listing posts.
        - `PostDetailSerializer` for viewing detailed information of a post.
    - The `perform_create` method ensures that the author of the post is set to the currently authenticated user.
        - notify all author followers for new post.
    """
    queryset = Post.objects.filter(
        status=StatusChoices.PUBLISHED  # Only show published posts
    ).order_by('-created_at')
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PostFilter  # Custom filter class for filtering posts

    def get_serializer_class(self):
        """
        Returns the serializer class based on the action:
        - For 'retrieve' action, it returns PostDetailSerializer.
        - For other actions like 'create' or 'update', it returns PostListSerializer.
        """
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer  # Fallback or for other actions like create/update

    def perform_create(self, serializer):
        new_post = serializer.save(author=self.request.user)
        notify_followers.delay(new_post.id)  # Notify user followers for new post, using celery


class CommentCreateView(CreateModelMixin, generics.GenericAPIView):
    """
    View for creating a new comment and adding replies to existing comments.

    It checks whether the user has already commented on the post
    and enforces the requirement of a `post_id` for creating comments.

    If a comment is a reply, it links the comment to its parent.
    The view also enforces user authentication or read-only permissions.
    """
    queryset = Comment.objects.filter(
        status=StatusChoices.PUBLISHED  # Query only published comments
    ).order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Handles the comment creation logic, including:
        - Ensuring a `post_id` is provided.
        - Handling replies by setting the `parent` field if a `parent_id` is provided.
        - Check if the user has already commented on the post before saving.
        """
        parent_id = self.request.data.get("parent_id")
        post_id = self.request.data.get("post_id")
        user = self.request.user

        # Ensure a post ID is provided
        if not post_id:
            raise ValidationError({
                "post_id": "This field is required."
            })

        # If there's a reply comment, find it and set it as the parent
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            serializer.save(
                parent=parent_comment,
                author=user,
                post_id=post_id
            )
        else:
            # Save as a normal comment if there's no parent
            serializer.save(
                author=user,
                post_id=post_id
            )

        return super().perform_create(serializer)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for creating new comments and replies.
        """
        return self.create(request, *args, **kwargs)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a single comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]


class ReactionToggleView(APIView):
    """
    View for toggling user reactions (like/dislike) on posts or comments.

    This view allows users to:
    - Add a reaction to a post or comment (like/dislike).
    - Remove a reaction if the user clicks on the same reaction again.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Handle POST requests for adding, updating, or removing a reaction.

        1. Validate the incoming reaction data using the `ReactionSerializer`.
        2. Check if the user has already reacted to the post or comment.
        3. If the reaction exists and matches the new one, remove it.
        4. If the reaction type is different, update the existing reaction.
        5. If no existing reaction, create a new one.
        """
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user

        # Check if the user has already reacted to this post or comment
        user_reaction = user.reactions.filter(
            Q(post=data.get('post')) | Q(comment=data.get('comment'))
        ).first()

        #
        if user_reaction:
            # If the reaction matches the new one, remove it
            if user_reaction.reaction_type == data['reaction']:
                user_reaction.delete()

                return Response({
                    "message": "Reaction removed."
                }, status=status.HTTP_200_OK)

            # If the reaction is different, update the existing one
            user_reaction.reaction_type = data['reaction']
            user_reaction.save()

            return Response({
                "message": "Reaction updated."
            }, status=status.HTTP_200_OK)

        # If no existing reaction, create a new one
        reaction = serializer.save(user=user)
        return Response(
            ReactionSerializer(reaction).data,
            status=status.HTTP_201_CREATED
        )


class TagView(generics.ListAPIView):
    """
    View to retrieve all tags.
    Also, can filter by tags name.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', ]
