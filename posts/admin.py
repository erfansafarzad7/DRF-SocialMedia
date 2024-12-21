from django.contrib import admin
from .models import Post, Comment, Reaction, Tag
from django.utils.html import mark_safe


class TagInline(admin.TabularInline):
    model = Tag.posts.through
    autocomplete_fields = ['tag']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'status', 'updated_at', 'image_thumbnail')
    list_filter = ('created_at', 'author')
    search_fields = ('id', 'title', 'content')
    autocomplete_fields = ('author', )
    inlines = [TagInline]

    # show images in admin
    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')  # show images with size 50x50
        return "No Image"
    image_thumbnail.short_description = 'Image'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'status', 'created_at')
    search_fields = ('content', 'author__username', 'author__id', 'post__id')
    list_filter = ('created_at', 'author')
    autocomplete_fields = ('parent', 'post', 'author')


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('id', 'user__username', 'post__id')
    ordering = ('-created_at',)
    autocomplete_fields = ('user', 'post', 'comment')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name', )
    autocomplete_fields = ('posts', )
