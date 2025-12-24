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
        ('system', 'System'),
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


class AutomatedResponse(models.Model):
    """Automated response rules for chat"""
    TRIGGER_TYPES = [
        ('keyword', 'Keyword Match'),
        ('greeting', 'Greeting Message'),
        ('first_message', 'First Message (Welcome)'),
        ('offline', 'All Admins Offline'),
        ('business_hours', 'Outside Business Hours'),
    ]
    
    name = models.CharField(max_length=200, help_text="Internal name for this automated response")
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    keywords = models.TextField(
        blank=True, 
        help_text="Comma-separated keywords to match (for keyword trigger type)"
    )
    response_message = models.TextField(help_text="The automated message to send")
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(
        default=0, 
        help_text="Higher priority responses are checked first"
    )
    delay_seconds = models.IntegerField(
        default=0,
        help_text="Delay in seconds before sending the automated response (0 for immediate)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = 'Automated Response'
        verbose_name_plural = 'Automated Responses'
    
    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"
    
    def get_keywords_list(self):
        """Return list of keywords"""
        if self.keywords:
            return [k.strip().lower() for k in self.keywords.split(',') if k.strip()]
        return []
    
    def matches_message(self, message_content):
        """Check if this automated response should trigger for given message"""
        if not self.is_active:
            return False
        
        if self.trigger_type == 'keyword':
            keywords = self.get_keywords_list()
            message_lower = message_content.lower()
            return any(keyword in message_lower for keyword in keywords)
        
        return False


class AutomatedResponseLog(models.Model):
    """Track when automated responses are sent"""
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='automated_responses')
    automated_response = models.ForeignKey(AutomatedResponse, on_delete=models.SET_NULL, null=True)
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, related_name='automated_response_log')
    trigger_message_content = models.TextField(help_text="The customer message that triggered this response")
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Automated Response Log'
        verbose_name_plural = 'Automated Response Logs'
    
    def __str__(self):
        return f"Auto-response in {self.chat_session} at {self.sent_at}"
