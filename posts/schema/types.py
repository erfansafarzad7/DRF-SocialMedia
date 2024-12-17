from graphene_django import DjangoObjectType
from posts.models import Post, Comment, Reaction, Tag, StatusChoices, ReactionChoices
from django.contrib.auth import get_user_model

import graphene

User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username")


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"

    author = graphene.Field(lambda: UserType)  # Foreignkey field

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
