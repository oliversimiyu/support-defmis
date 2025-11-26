from django.db import models
from django.contrib.auth.models import User
import uuid


class ChatSession(models.Model):
    """Represents a chat conversation between a customer and admin"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_id = models.CharField(max_length=50, unique=True)  # Auto-generated client ID
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat {self.id} - {self.customer_name or self.customer_id}"
    
    @property
    def unread_messages_count(self):
        return self.messages.filter(is_read=False, sender_type='customer').count()


class Message(models.Model):
    """Individual message in a chat session"""
    SENDER_TYPES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES)
    sender_name = models.CharField(max_length=100, blank=True, null=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender_type}: {self.content[:50]}..."


class ChatWidget(models.Model):
    """Configuration for the embeddable chat widget"""
    name = models.CharField(max_length=100, default='Chat Widget')
    welcome_message = models.TextField(default='Hi there! How can we help you today?')
    primary_color = models.CharField(max_length=7, default='#007bff')  # Hex color
    widget_position = models.CharField(
        max_length=20, 
        choices=[('bottom-right', 'Bottom Right'), ('bottom-left', 'Bottom Left')],
        default='bottom-right'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Chat Widget Configuration'
        verbose_name_plural = 'Chat Widget Configurations'
    
    def __str__(self):
        return self.name
