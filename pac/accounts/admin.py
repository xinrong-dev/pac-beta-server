from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Member, Genre, Friendship, Blockship, Banner

# Register your models here.


class MemberAdmin(UserAdmin):
    list_display = (
        'email',
        'user_id',
        'username',
        'is_active',
        'social_type',
        'language',
        'date_joined',
        'is_staff')
    ordering = ('user_id',)
    fieldsets = (
        (None, {'fields': ('username', 'user_id', 'password')}),
        (_('Personal info'), {'fields': ('firebase_id', 'social_type', 'language', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


class GenreAdmin(admin.ModelAdmin):
    ordering = ['order']
    list_display = (
        'name',
        'parent',
        'sub_order',
        'depth',
        'order',
        'is_shown',
        'created_at',
    )
    search_fields = ['name']


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'followee', 'created_at')
    list_filter = ('follower', )


class BlockshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'blocked', 'created_at')
    list_filter = ('blocker', )


class BannerAdmin(admin.ModelAdmin):
    ordering = ['order']
    list_display = ('link', 'get_image', 'order', 'is_shown', 'created_at', )


admin.site.register(Member, MemberAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Friendship, FriendshipAdmin)
admin.site.register(Blockship, BlockshipAdmin)
admin.site.register(Banner, BannerAdmin)
