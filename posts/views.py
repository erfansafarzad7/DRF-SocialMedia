from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.mixins import CreateModelMixin
from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from .models import StatusChoices, ReactionChoices, Post, Comment, Reaction, Tag
from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer, ReactionSerializer, TagSerializer
from utils import custom_permissions
from .filters import PostFilter


class PostViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing posts.
    """

    queryset = Post.objects.filter(status=StatusChoices.PUBLISHED).order_by('-created_at')
    permission_classes = [custom_permissions.IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PostFilter  # Connect the filter

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer  # Fallback or for other actions like create/update

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentCreateView(generics.GenericAPIView, CreateModelMixin):
    """
    View for creating a new comment and adding replies to existing comments.
    """

    queryset = Comment.objects.filter(status=StatusChoices.PUBLISHED).order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Handle comment creation with optional reply functionality.
        Check if the user has already commented on the post before saving.
        If the comment is a reply, set the parent.
        """
        parent_id = self.request.data.get("parent_id")
        post_id = self.request.data.get("post_id")
        user = self.request.user

        if not post_id:
            raise ValidationError({"post_id": "This field is required."})

        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            serializer.save(parent=parent_comment, author=user, post_id=post_id)
        else:
            # Save as a normal comment if there's no parent
            serializer.save(author=user, post_id=post_id)

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, custom_permissions.IsAuthorOrReadOnly]


class ReactionToggleView(APIView):
    """
    View to toggle like/dislike for a post or comment.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        request_reaction_type = request.data.get('reaction')
        post_id = request.data.get('post_id')
        comment_id = request.data.get('comment_id')

        # Validate input
        if not request_reaction_type or request_reaction_type not in [ReactionChoices.LIKE, ReactionChoices.DISLIKE]:
            return Response({"reaction": "Invalid reaction type. Use 'like' or 'dislike'."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not post_id and not comment_id:
            return Response({"message": "You must provide either a post ID or a comment ID."},
                            status=status.HTTP_400_BAD_REQUEST)
        if post_id and comment_id:
            return Response({"message": "You cannot react to post and comment at same time."},
                            status.HTTP_400_BAD_REQUEST)

        # Check for existing reaction
        user_reactions = user.reactions.filter(Q(post_id=post_id) | Q(comment_id=comment_id)).first()

        if user_reactions:  # If user has reacted before

            if user_reactions.reaction_type == request_reaction_type:
                # If the same reaction exists, delete it
                user_reactions.delete()
                return Response({"message": f"{request_reaction_type.capitalize()} removed."},
                                status=status.HTTP_200_OK)
            else:
                # Update the reaction type
                user_reactions.reaction_type = request_reaction_type
                user_reactions.save()
                return Response({"message": f"Reaction updated to {request_reaction_type}."},
                                status=status.HTTP_200_OK)

        else:
            # Create a new reaction
            try:
                reaction = Reaction.objects.create(
                    user=user,
                    post_id=post_id,
                    comment_id=comment_id,
                    reaction_type=request_reaction_type
                )

                serializer = ReactionSerializer(reaction)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except ValueError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TagView(generics.ListAPIView):
    """
    View to retrieve all tags with filtering.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', ]
