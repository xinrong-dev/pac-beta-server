from django.contrib import admin
from .models import CcSetting, Work, MediaImage, Favorite, Comment

# Register your models here.
class CcSettingAdmin(admin.ModelAdmin):
    list_display = ('en_name', 'cc', 'image', 'image_container')

class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'creator', 'cc_setting', 'url', 'created_at', )
    filter_horizontal = ('images', 'collaborators', )
    fields = ('title', 'status', 'creator', 'collaborators', 'url', 'tags', 'cc_setting', 'images', 'image_container', )
    readonly_fields = ('image_container', )
    search_fields = ['title']

class MediaAdmin(admin.ModelAdmin):
    list_display = ('uri', )

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('name', 'liker', 'created_at')
    list_filter = ('liker', )

class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'commentor', 'work', 'created_at', )
    list_filter = ('commentor', )

admin.site.register(CcSetting, CcSettingAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(MediaImage, MediaAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Comment, CommentAdmin)