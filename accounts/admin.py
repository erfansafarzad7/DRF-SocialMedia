from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Follow, Notification


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('id', 'mobile', 'username', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('mobile', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
        ('OTP Info', {'fields': ('otp', 'otp_created')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'username', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )
    search_fields = ('id', 'mobile', 'username')
    ordering = ('mobile',)
    filter_horizontal = ('groups', 'user_permissions',)
    list_display_links = ('id', 'mobile', 'username')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)
    autocomplete_fields = ('follower', 'following')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'is_read']
    list_filter = ['is_read', 'user']
