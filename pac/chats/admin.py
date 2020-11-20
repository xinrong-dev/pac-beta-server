from django.contrib import admin
from .models import Message


# Register your models here.
class MessageAdmin(admin.ModelAdmin):
    list_display = ['content', 'image', 'sender', 'receiver', 'created_at', 'is_read']
    list_filter = ['sender', 'receiver']

admin.site.register(Message, MessageAdmin)
