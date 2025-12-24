from django.contrib import admin
from .models import ChatSession, Message, ChatWidget, AutomatedResponse, AutomatedResponseLog


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


@admin.register(AutomatedResponse)
class AutomatedResponseAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'is_active', 'priority', 'delay_seconds', 'created_at']
    list_filter = ['trigger_type', 'is_active', 'created_at']
    search_fields = ['name', 'keywords', 'response_message']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active', 'priority')
        }),
        ('Trigger Configuration', {
            'fields': ('trigger_type', 'keywords')
        }),
        ('Response Settings', {
            'fields': ('response_message', 'delay_seconds')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help text
        form.base_fields['keywords'].help_text = (
            'Only used for "Keyword Match" trigger type. '
            'Enter comma-separated keywords (e.g., "pricing, cost, price, payment")'
        )
        return form


@admin.register(AutomatedResponseLog)
class AutomatedResponseLogAdmin(admin.ModelAdmin):
    list_display = ['chat_session', 'automated_response', 'trigger_preview', 'sent_at']
    list_filter = ['sent_at', 'automated_response']
    search_fields = ['trigger_message_content', 'chat_session__customer_name']
    readonly_fields = ['chat_session', 'automated_response', 'message', 'trigger_message_content', 'sent_at']
    
    def trigger_preview(self, obj):
        return obj.trigger_message_content[:50] + '...' if len(obj.trigger_message_content) > 50 else obj.trigger_message_content
    trigger_preview.short_description = 'Trigger Message'
    
    def has_add_permission(self, request):
        # Logs are created automatically, not manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Logs are read-only
        return False
