import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatSession, Message
import uuid


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.customer_id = self.scope['url_route']['kwargs']['customer_id']
        self.room_group_name = f'chat_{self.customer_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = text_data_json['message']
            sender_type = text_data_json['sender_type']
            sender_name = text_data_json.get('sender_name', 'Anonymous')
            
            # Save message to database
            chat_session, message_obj = await self.save_message(
                self.customer_id, message, sender_type, sender_name
            )
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_type': sender_type,
                    'sender_name': sender_name,
                    'timestamp': message_obj.timestamp.isoformat(),
                    'message_id': str(message_obj.id),
                }
            )
            
            # Also send to admin dashboard
            await self.channel_layer.group_send(
                'admin_dashboard',
                {
                    'type': 'new_message_notification',
                    'chat_session_id': str(chat_session.id),
                    'customer_id': self.customer_id,
                    'message': message,
                    'sender_type': sender_type,
                    'sender_name': sender_name,
                    'timestamp': message_obj.timestamp.isoformat(),
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender_type = event['sender_type']
        sender_name = event['sender_name']
        timestamp = event['timestamp']
        message_id = event['message_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender_type': sender_type,
            'sender_name': sender_name,
            'timestamp': timestamp,
            'message_id': message_id,
        }))

    @database_sync_to_async
    def save_message(self, customer_id, message, sender_type, sender_name):
        # Get or create chat session
        chat_session, created = ChatSession.objects.get_or_create(
            customer_id=customer_id,
            defaults={'status': 'open'}
        )
        
        # Create message
        message_obj = Message.objects.create(
            chat_session=chat_session,
            content=message,
            sender_type=sender_type,
            sender_name=sender_name
        )
        
        return chat_session, message_obj


class AdminDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Only allow authenticated users (admins)
        if self.scope["user"].is_anonymous or not self.scope["user"].is_staff:
            await self.close()
        else:
            self.room_group_name = 'admin_dashboard'
            
            # Join admin dashboard group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'admin_message':
            customer_id = text_data_json['customer_id']
            message = text_data_json['message']
            sender_name = text_data_json.get('sender_name', self.scope["user"].get_full_name() or self.scope["user"].username)
            
            # Save message to database
            chat_session, message_obj = await self.save_admin_message(
                customer_id, message, sender_name
            )
            
            # Send message to specific customer room
            customer_room = f'chat_{customer_id}'
            await self.channel_layer.group_send(
                customer_room,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_type': 'admin',
                    'sender_name': sender_name,
                    'timestamp': message_obj.timestamp.isoformat(),
                    'message_id': str(message_obj.id),
                }
            )

    async def new_message_notification(self, event):
        # Send notification to admin dashboard
        await self.send(text_data=json.dumps({
            'type': 'new_message_notification',
            'chat_session_id': event['chat_session_id'],
            'customer_id': event['customer_id'],
            'message': event['message'],
            'sender_type': event['sender_type'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def save_admin_message(self, customer_id, message, sender_name):
        # Get chat session
        chat_session = ChatSession.objects.get(customer_id=customer_id)
        
        # Mark customer messages as read
        Message.objects.filter(
            chat_session=chat_session,
            sender_type='customer',
            is_read=False
        ).update(is_read=True)
        
        # Create admin message
        message_obj = Message.objects.create(
            chat_session=chat_session,
            content=message,
            sender_type='admin',
            sender_name=sender_name
        )
        
        return chat_session, message_obj