from posts.models import Post, Tag, StatusChoices
from .types import PostType, TagType

import graphene



class Query(graphene.ObjectType):
    posts = graphene.List(PostType, author_id=graphene.Int())
    post = graphene.Field(PostType, id=graphene.Int(required=True))
    tags = graphene.List(TagType)

    def resolve_posts(self, info, author_id=None):
        queryset = Post.objects.filter(status=StatusChoices.PUBLISHED)

        if author_id:
            queryset = queryset.filter(author_id=author_id)

        return queryset

    def resolve_post(self, info, id):
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            return None

    def resolve_tags(self, info):
        return Tag.objects.all()
