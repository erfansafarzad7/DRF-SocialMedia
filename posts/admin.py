from django.contrib import admin
from .models import Post, Comment, Like, Tag
from django.utils.html import mark_safe


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'updated_at', 'image_thumbnail')
    list_filter = ('created_at', 'author')
    search_fields = ('id', 'title', 'content')
    autocomplete_fields = ('author', )

    # show images in admin
    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')  # show images with size 50x50
        return "No Image"
    image_thumbnail.short_description = 'Image'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')
    search_fields = ('content', 'author__username', 'author__id', 'post__id')
    list_filter = ('created_at', 'author')
    autocomplete_fields = ('post', 'author')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'comment', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'user__id', 'post__id', 'comment__id')
    autocomplete_fields = ('user', 'post', 'comment')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
