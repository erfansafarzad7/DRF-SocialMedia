from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, OTPVerification, Follow, Notification


class NotificationsInline(admin.TabularInline):
    model = Notification
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('id', 'mobile', 'username', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('id', 'mobile', 'username')
    ordering = ('id',)
    filter_horizontal = ('groups', 'user_permissions',)
    list_display_links = ('id', 'mobile', 'username')
    inlines = [NotificationsInline]

    fieldsets = (
        (None, {'fields': ('mobile', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'username', 'password1', 'password2', 'is_active', 'is_staff')
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'code', 'created_at')
    search_fields = ('mobile', 'code')
    list_filter = ('created_at', )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)
    autocomplete_fields = ('follower', 'following')
    raw_id_fields = ('follower', 'following')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'is_read']
    list_filter = ['is_read', 'user', 'created_at']
    autocomplete_fields = ['user']
