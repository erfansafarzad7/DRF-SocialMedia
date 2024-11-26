from rest_framework import serializers
from .models import Post, Comment, Like, Tag


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['post', 'author', 'status', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'posts']


class PostListSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()
    author = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='username',
        read_only=True
    )
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'  # Return the name of the tag
    )

    class Meta:
        model = Post
        fields = ['id', 'image', 'caption', 'author', 'author_username', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['status']

    def get_author_username(self, obj):
        return obj.author.username


class PostDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()
    author = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='username',
        read_only=True
    )
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    comments = serializers.SerializerMethodField()
    likes = serializers.SlugRelatedField(many=True, read_only=True, slug_field='user__username')

    class Meta:
        model = Post
        fields = [
            'id', 'image', 'caption', 'author', 'author_username', 'tags',
            'comments', 'likes', 'created_at', 'updated_at'
        ]

    def get_author_username(self, obj):
        return obj.author.username

    def get_comments(self, obj):
        published_comments = obj.comments.filter(status=1)  # Filter published comments
        return CommentSerializer(published_comments, many=True).data