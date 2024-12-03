from django.db.models import Count, Q
from rest_framework import serializers
from .models import StatusChoices, Post, Comment, Reaction, Tag, ReactionChoices


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments, including replies and reaction counts (likes/dislikes).
    Handles nested replies and ensures only published comments are retrieved.
    """

    author = serializers.ReadOnlyField(source='author.username')
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'post', 'author', 'content', 'replies', 'likes_count', 'dislikes_count', 'created_at']
        read_only_fields = ['post', 'author', 'status', 'replies', 'created_at']

    def get_replies(self, obj):
        if obj.replies:
            # Retrieve the replies queryset directly from the related name
            replies = obj.replies.filter(status=StatusChoices.PUBLISHED)
            return CommentSerializer(replies, many=True, context=self.context).data
        return []

    def get_likes_count(self, obj):
        return obj.reactions.filter(comment=obj, reaction_type='like').count()

    def get_dislikes_count(self, obj):
        return obj.reactions.filter(comment=obj, reaction_type='dislike').count()


class ReactionSerializer(serializers.ModelSerializer):
    """
    Serializer for user reactions (like/dislike) on posts and comments.
    """

    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'post', 'comment', 'reaction_type', 'created_at']
        read_only_fields = ['user', 'created_at']


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tags associated with posts.
    Supports retrieving tag names and their related posts.
    """

    class Meta:
        model = Tag
        fields = ['id', 'name', 'posts']


class PostListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing posts with author, tags, and creation details.
    Includes validation for a maximum of 5 tags during post creation.
    """

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
    """
    Serializer for detailed post view, including comments, tags, and reaction counts.
    Handles nested comments and filters only published ones.
    """

    author_username = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
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
        fields = [
            'id', 'image', 'caption', 'author', 'author_username', 'tags',
            'comments', 'likes_count', 'dislikes_count', 'created_at', 'updated_at'
        ]

    def get_author_username(self, obj):
        return obj.author.username

    def get_comments(self, obj):
        published_comments = obj.comments.filter(status=StatusChoices.PUBLISHED)  # Filter published comments
        return CommentSerializer(published_comments, many=True).data

    def get_likes_count(self, obj):
        return obj.reactions.filter(post=obj, reaction_type='like').count()

    def get_dislikes_count(self, obj):
        return obj.reactions.filter(post=obj, reaction_type='dislike').count()
