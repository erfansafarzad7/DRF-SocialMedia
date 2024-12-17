from posts.models import Post, Tag, StatusChoices
from .types import PostType, TagType

import graphene


class Query(graphene.ObjectType):
    """
    Root query class for retrieving posts and tags.

    Fields:
        posts: A list of published posts, optionally filtered by author ID.
        post: A single post by ID.
        tags: A list of all tags.
    """
    posts = graphene.List(PostType, author_id=graphene.Int())
    post = graphene.Field(PostType, id=graphene.Int(required=True))
    tags = graphene.List(TagType)

    def resolve_posts(self, info, author_id=None):
        """
        Resolves the list of posts, optionally filtered by the author ID.
        """
        queryset = Post.objects.filter(
            status=StatusChoices.PUBLISHED  # Only get published posts
        )

        if author_id:
            queryset = queryset.filter(
                author_id=author_id  # Filter by author if provided
            )

        return queryset

    def resolve_post(self, info, id):
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            return None

    def resolve_tags(self, info):
        return Tag.objects.all()
