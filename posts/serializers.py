from rest_framework import serializers
from .models import StatusChoices, Post, Comment, Like, Tag


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
        queryset=Tag.objects.all(),
        slug_field='name',  # Return the name of the tag
        required=False
    )

    class Meta:
        model = Post
        fields = ['id', 'image', 'caption', 'author', 'author_username', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['status']

    def get_author_username(self, obj):
        return obj.author.username

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        print(tags_data)
        if len(tags_data) > 5:
            raise serializers.ValidationError({'tags': 'Too many tags. it must be less or equal 5 tags.'})

        for tag_name in tags_data:
            tag = Tag.objects.get(name=tag_name)
            post.tags.add(tag)

        return post


class PostDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
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
    likes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='user__username'
    )

    class Meta:
        model = Post
        fields = [
            'id', 'image', 'caption', 'author', 'author_username', 'tags',
            'comments', 'likes', 'created_at', 'updated_at'
        ]

    def get_author_username(self, obj):
        return obj.author.username

    def get_comments(self, obj):
        published_comments = obj.comments.filter(status=StatusChoices.PUBLISHED)  # Filter published comments
        return CommentSerializer(published_comments, many=True).data
