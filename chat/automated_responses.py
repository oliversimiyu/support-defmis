"""
Service module for handling automated responses
"""
from django.utils import timezone
from django.contrib.auth.models import User
from .models import AutomatedResponse, AutomatedResponseLog, ChatSession, Message
import asyncio
from channels.db import database_sync_to_async


class AutomatedResponseService:
    """Service to handle automated responses"""
    
    @staticmethod
    @database_sync_to_async
    def get_matching_responses(message_content, chat_session, trigger_type=None):
        """
        Find automated responses that match the given message
        Returns list of AutomatedResponse objects
        """
        # Get active responses
        responses = AutomatedResponse.objects.filter(is_active=True)
        
        if trigger_type:
            responses = responses.filter(trigger_type=trigger_type)
        
        matching_responses = []
        
        for response in responses:
            if response.trigger_type == 'keyword':
                if response.matches_message(message_content):
                    matching_responses.append(response)
            elif response.trigger_type == trigger_type:
                matching_responses.append(response)
        
        # Sort by priority
        matching_responses.sort(key=lambda x: x.priority, reverse=True)
        
        return matching_responses
    
    @staticmethod
    @database_sync_to_async
    def should_send_first_message_response(chat_session):
        """
        Check if we should send a first message/welcome automated response
        """
        # Only send if it's the first customer message
        message_count = Message.objects.filter(
            chat_session=chat_session,
            sender_type='customer'
        ).count()
        
        return message_count == 1
    
    @staticmethod
    @database_sync_to_async
    def check_admins_online():
        """
        Check if any admin users are currently online/active
        This is a simplified version - in production you'd track online status
        """
        # For now, check if there are any staff users
        # In production, implement proper online tracking
        return User.objects.filter(is_staff=True, is_active=True).exists()
    
    @staticmethod
    @database_sync_to_async
    def is_business_hours():
        """
        Check if current time is within business hours
        This is a simplified version
        """
        now = timezone.now()
        # Business hours: Monday-Friday, 9 AM - 5 PM
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        hour = now.hour
        return 9 <= hour < 17
    
    @staticmethod
    @database_sync_to_async
    def create_automated_message(chat_session, automated_response, trigger_message_content):
        """
        Create an automated message and log it
        Returns the created Message object
        """
        # Create the automated message
        message_obj = Message.objects.create(
            chat_session=chat_session,
            content=automated_response.response_message,
            sender_type='system',
            sender_name='Auto-response'
        )
        
        # Log the automated response
        AutomatedResponseLog.objects.create(
            chat_session=chat_session,
            automated_response=automated_response,
            message=message_obj,
            trigger_message_content=trigger_message_content
        )
        
        return message_obj
    
    @staticmethod
    @database_sync_to_async
    def get_chat_session(customer_id):
        """Get chat session by customer_id"""
        try:
            return ChatSession.objects.get(customer_id=customer_id)
        except ChatSession.DoesNotExist:
            return None
    
    @staticmethod
    async def process_automated_responses(customer_id, message_content, channel_layer, room_group_name):
        """
        Process and send automated responses to CLIENTS/CUSTOMERS
        
        This is triggered when a customer sends a message. It checks all active 
        automated response rules and sends matching responses back to the CUSTOMER
        via their WebSocket connection.
        
        Args:
            customer_id: The customer's unique identifier
            message_content: The message sent by the customer
            channel_layer: Django Channels layer for WebSocket communication
            room_group_name: The customer's chat room (f'chat_{customer_id}')
        
        The responses are sent TO THE CUSTOMER, not to admins.
        Admins only receive notifications about the automated responses.
        """
        chat_session = await AutomatedResponseService.get_chat_session(customer_id)
        if not chat_session:
            return
        
        responses_to_send = []
        
        # Check for first message (welcome) response
        is_first_message = await AutomatedResponseService.should_send_first_message_response(chat_session)
        if is_first_message:
            first_msg_responses = await AutomatedResponseService.get_matching_responses(
                message_content, chat_session, trigger_type='first_message'
            )
            responses_to_send.extend(first_msg_responses)
        
        # Check for greeting responses
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in message_content.lower() for greeting in greeting_keywords):
            greeting_responses = await AutomatedResponseService.get_matching_responses(
                message_content, chat_session, trigger_type='greeting'
            )
            responses_to_send.extend(greeting_responses)
        
        # Check for keyword matches
        keyword_responses = await AutomatedResponseService.get_matching_responses(
            message_content, chat_session, trigger_type='keyword'
        )
        responses_to_send.extend(keyword_responses)
        
        # Check if admins are offline
        admins_online = await AutomatedResponseService.check_admins_online()
        if not admins_online:
            offline_responses = await AutomatedResponseService.get_matching_responses(
                message_content, chat_session, trigger_type='offline'
            )
            responses_to_send.extend(offline_responses)
        
        # Check business hours
        is_biz_hours = await AutomatedResponseService.is_business_hours()
        if not is_biz_hours:
            biz_hours_responses = await AutomatedResponseService.get_matching_responses(
                message_content, chat_session, trigger_type='business_hours'
            )
            responses_to_send.extend(biz_hours_responses)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_responses = []
        for resp in responses_to_send:
            if resp.id not in seen:
                seen.add(resp.id)
                unique_responses.append(resp)
        
        # Send the automated responses
        for auto_response in unique_responses:
            # Apply delay if specified
            if auto_response.delay_seconds > 0:
                await asyncio.sleep(auto_response.delay_seconds)
            
            # Create the automated message in database
            message_obj = await AutomatedResponseService.create_automated_message(
                chat_session, auto_response, message_content
            )
            
            # Send automated response to the CLIENT/CUSTOMER via their WebSocket room
            # room_group_name = f'chat_{customer_id}' - this is the customer's chat room
            await channel_layer.group_send(
                room_group_name,
                {
                    'type': 'chat_message',
                    'message': auto_response.response_message,
                    'sender_type': 'system',
                    'sender_name': 'Auto-response',
                    'timestamp': message_obj.timestamp.isoformat(),
                    'message_id': str(message_obj.id),
                }
            )
            
            # Also notify admin dashboard (for admin visibility only, not for sending to admins)
            await channel_layer.group_send(
                'admin_dashboard',
                {
                    'type': 'new_message_notification',
                    'chat_session_id': str(chat_session.id),
                    'customer_id': customer_id,
                    'message': auto_response.response_message,
                    'sender_type': 'system',
                    'sender_name': 'Auto-response',
                    'timestamp': message_obj.timestamp.isoformat(),
                }
            )
