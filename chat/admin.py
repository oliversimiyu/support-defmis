from django.contrib import admin
from .models import ChatSession, Message, ChatWidget


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_id', 'status', 'unread_messages_count', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['customer_name', 'customer_email', 'customer_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def unread_messages_count(self, obj):
        return obj.unread_messages_count
    unread_messages_count.short_description = 'Unread Messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'chat_session', 'sender_type', 'sender_name', 'content_preview', 'is_read', 'timestamp']
    list_filter = ['sender_type', 'is_read', 'timestamp']
    search_fields = ['content', 'sender_name']
    readonly_fields = ['id', 'timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(ChatWidget)
class ChatWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'widget_position', 'primary_color', 'created_at']
    list_filter = ['is_active', 'widget_position', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
