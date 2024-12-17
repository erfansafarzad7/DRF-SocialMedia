from graphene_django import DjangoObjectType
from posts.models import Post, Comment, Reaction, Tag, StatusChoices, ReactionChoices
from django.contrib.auth import get_user_model

import graphene

User = get_user_model()


# class StatusChoicesType(graphene.Enum):
#     DRAFT = StatusChoices.DRAFT
#     PUBLISHED = StatusChoices.PUBLISHED
#
#
# class ReactionChoicesType(graphene.Enum):
#     LIKE = ReactionChoices.LIKE
#     DISLIKE = ReactionChoices.DISLIKE
#
#
# class TagType(DjangoObjectType):
#     class Meta:
#         model = Tag
#         fields = ('id', 'name', 'posts')
#
#
# class ReactionType(DjangoObjectType):
#     reaction_type = graphene.Field(ReactionChoicesType)
#
#     class Meta:
#         model = Reaction
#         fields = ('id', 'user', 'post', 'comment',
#                   'reaction_type', 'created_at')
#
#
# class CommentType(DjangoObjectType):
#     class Meta:
#         model = Comment
#         fields = ('id', 'parent', 'post', 'author', 'content',
#                   'status', 'created_at', 'replies', 'reactions')
#
#
# class PostType(DjangoObjectType):
#     status = graphene.Field(StatusChoicesType)
#     comments = graphene.List(CommentType)
#     reactions = graphene.List(ReactionType)
#     tags = graphene.List(TagType)
#
#     class Meta:
#         model = Post
#         fields = ('id', 'image', 'caption', 'author', 'status', 'created_at',
#                   'updated_at', 'comments', 'reactions', 'tags')


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username")


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"

    author = graphene.Field(lambda: UserType)

    def resolve_author(self, info):
        return self.author


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = "__all__"


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"


class ReactionType(DjangoObjectType):
    class Meta:
        model = Reaction
        fields = "__all__"
