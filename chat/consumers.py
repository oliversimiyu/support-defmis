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
            
        elif message_type == 'close_conversation':
            # Close the conversation
            chat_session = await self.close_conversation(
                self.customer_id, text_data_json.get('sender_name', 'Customer')
            )
            
            # Notify both customer and admin
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'conversation_closed',
                    'closed_by': text_data_json.get('sender_name', 'Customer'),
                    'timestamp': chat_session.updated_at.isoformat(),
                }
            )
            
            # Notify admin dashboard
            await self.channel_layer.group_send(
                'admin_dashboard',
                {
                    'type': 'conversation_status_changed',
                    'chat_session_id': str(chat_session.id),
                    'customer_id': self.customer_id,
                    'status': 'closed',
                    'closed_by': text_data_json.get('sender_name', 'Customer'),
                    'timestamp': chat_session.updated_at.isoformat(),
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

    # Handle conversation closure
    async def conversation_closed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'conversation_closed',
            'closed_by': event['closed_by'],
            'timestamp': event['timestamp'],
        }))
    
    # Handle conversation reopening
    async def conversation_reopened(self, event):
        await self.send(text_data=json.dumps({
            'type': 'conversation_reopened',
            'reopened_by': event['reopened_by'],
            'timestamp': event['timestamp'],
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

    @database_sync_to_async
    def close_conversation(self, customer_id, closed_by):
        # Get chat session and close it
        chat_session = ChatSession.objects.get(customer_id=customer_id)
        chat_session.status = 'closed'
        chat_session.save()
        
        # Add a system message about the closure
        Message.objects.create(
            chat_session=chat_session,
            content=f'Conversation closed by {closed_by}',
            sender_type='system',
            sender_name='System'
        )
        
        return chat_session


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
            
        elif message_type == 'admin_close_conversation':
            customer_id = text_data_json['customer_id']
            admin_name = self.scope["user"].get_full_name() or self.scope["user"].username
            
            # Close the conversation
            chat_session = await self.close_admin_conversation(customer_id, admin_name)
            
            # Notify customer
            customer_room = f'chat_{customer_id}'
            await self.channel_layer.group_send(
                customer_room,
                {
                    'type': 'conversation_closed',
                    'closed_by': admin_name,
                    'timestamp': chat_session.updated_at.isoformat(),
                }
            )
            
            # Notify admin dashboard
            await self.channel_layer.group_send(
                'admin_dashboard',
                {
                    'type': 'conversation_status_changed',
                    'chat_session_id': str(chat_session.id),
                    'customer_id': customer_id,
                    'status': 'closed',
                    'closed_by': admin_name,
                    'timestamp': chat_session.updated_at.isoformat(),
                }
            )
            
        elif message_type == 'admin_reopen_conversation':
            customer_id = text_data_json['customer_id']
            admin_name = self.scope["user"].get_full_name() or self.scope["user"].username
            
            # Reopen the conversation
            chat_session = await self.reopen_admin_conversation(customer_id, admin_name)
            
            # Notify customer
            customer_room = f'chat_{customer_id}'
            await self.channel_layer.group_send(
                customer_room,
                {
                    'type': 'conversation_reopened',
                    'reopened_by': admin_name,
                    'timestamp': chat_session.updated_at.isoformat(),
                }
            )
            
            # Notify admin dashboard
            await self.channel_layer.group_send(
                'admin_dashboard',
                {
                    'type': 'conversation_status_changed',
                    'chat_session_id': str(chat_session.id),
                    'customer_id': customer_id,
                    'status': 'open',
                    'reopened_by': admin_name,
                    'timestamp': chat_session.updated_at.isoformat(),
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

    async def conversation_status_changed(self, event):
        # Send conversation status change notification to admin dashboard
        response_data = {
            'type': 'conversation_status_changed',
            'chat_session_id': event['chat_session_id'],
            'customer_id': event['customer_id'],
            'status': event['status'],
            'timestamp': event['timestamp'],
        }
        
        # Add the appropriate field based on action
        if event['status'] == 'closed':
            response_data['closed_by'] = event.get('closed_by', 'Unknown')
        elif event['status'] == 'open':
            response_data['reopened_by'] = event.get('reopened_by', 'Unknown')
        
        await self.send(text_data=json.dumps(response_data))

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

    @database_sync_to_async
    def close_admin_conversation(self, customer_id, admin_name):
        # Get chat session and close it
        chat_session = ChatSession.objects.get(customer_id=customer_id)
        chat_session.status = 'closed'
        chat_session.save()
        
        # Add a system message about the closure
        Message.objects.create(
            chat_session=chat_session,
            content=f'Conversation closed by {admin_name}',
            sender_type='system',
            sender_name='System'
        )
        
        return chat_session
    
    @database_sync_to_async
    def reopen_admin_conversation(self, customer_id, admin_name):
        # Get chat session and reopen it
        chat_session = ChatSession.objects.get(customer_id=customer_id)
        chat_session.status = 'open'
        chat_session.save()
        
        # Add a system message about the reopening
        Message.objects.create(
            chat_session=chat_session,
            content=f'Conversation reopened by {admin_name}',
            sender_type='system',
            sender_name='System'
        )
        
        return chat_session