from rest_framework import serializers
from .models import ChatSession, Message, ChatWidget


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'sender_type', 'sender_name', 'attachment', 'is_read', 'timestamp']


class ChatSessionSerializer(serializers.ModelSerializer):
    unread_messages_count = serializers.ReadOnlyField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'customer_name', 'customer_email', 'customer_id', 'status', 
                 'created_at', 'updated_at', 'unread_messages_count', 'last_message']
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None


class ChatWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatWidget
        fields = ['name', 'welcome_message', 'primary_color', 'widget_position', 'is_active']