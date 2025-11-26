from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import ChatSession, Message, ChatWidget
from .serializers import ChatSessionSerializer, MessageSerializer, ChatWidgetSerializer
import json
import uuid


@api_view(['GET'])
@permission_classes([AllowAny])
def widget_config(request):
    """Get chat widget configuration"""
    try:
        widget = ChatWidget.objects.filter(is_active=True).first()
        if widget:
            serializer = ChatWidgetSerializer(widget)
            return Response(serializer.data)
        else:
            # Return default configuration
            return Response({
                'name': 'Chat Widget',
                'welcome_message': 'Hi there! How can we help you today?',
                'primary_color': '#007bff',
                'widget_position': 'bottom-right',
                'is_active': True
            })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def start_chat(request):
    """Initialize a new chat session or get existing one"""
    try:
        customer_id = request.data.get('customer_id')
        customer_name = request.data.get('customer_name', '')
        customer_email = request.data.get('customer_email', '')
        
        if not customer_id:
            customer_id = str(uuid.uuid4())
        
        # Get or create chat session
        chat_session, created = ChatSession.objects.get_or_create(
            customer_id=customer_id,
            defaults={
                'customer_name': customer_name,
                'customer_email': customer_email,
                'status': 'open'
            }
        )
        
        # Update customer info if provided
        if customer_name and not chat_session.customer_name:
            chat_session.customer_name = customer_name
        if customer_email and not chat_session.customer_email:
            chat_session.customer_email = customer_email
        chat_session.save()
        
        serializer = ChatSessionSerializer(chat_session)
        return Response({
            'chat_session': serializer.data,
            'customer_id': customer_id,
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def chat_history(request, customer_id):
    """Get chat history for a customer"""
    try:
        chat_session = get_object_or_404(ChatSession, customer_id=customer_id)
        messages = chat_session.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    except ChatSession.DoesNotExist:
        return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_message(request):
    """Send a message (used as fallback if WebSocket is not available)"""
    try:
        customer_id = request.data.get('customer_id')
        message_content = request.data.get('message')
        sender_type = request.data.get('sender_type', 'customer')
        sender_name = request.data.get('sender_name', 'Anonymous')
        
        if not customer_id or not message_content:
            return Response({'error': 'customer_id and message are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Get chat session
        chat_session = get_object_or_404(ChatSession, customer_id=customer_id)
        
        # Create message
        message = Message.objects.create(
            chat_session=chat_session,
            content=message_content,
            sender_type=sender_type,
            sender_name=sender_name
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except ChatSession.DoesNotExist:
        return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Admin API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_chat_sessions(request):
    """Get all chat sessions for admin dashboard"""
    try:
        sessions = ChatSession.objects.all()
        status_filter = request.GET.get('status')
        if status_filter:
            sessions = sessions.filter(status=status_filter)
        
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_chat_detail(request, session_id):
    """Get detailed chat session with messages"""
    try:
        chat_session = get_object_or_404(ChatSession, id=session_id)
        messages = chat_session.messages.all()
        
        # Mark customer messages as read
        Message.objects.filter(
            chat_session=chat_session,
            sender_type='customer',
            is_read=False
        ).update(is_read=True)
        
        session_serializer = ChatSessionSerializer(chat_session)
        messages_serializer = MessageSerializer(messages, many=True)
        
        return Response({
            'chat_session': session_serializer.data,
            'messages': messages_serializer.data
        })
    except ChatSession.DoesNotExist:
        return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_chat_status(request, session_id):
    """Update chat session status"""
    try:
        chat_session = get_object_or_404(ChatSession, id=session_id)
        new_status = request.data.get('status')
        
        if new_status in ['open', 'closed']:
            chat_session.status = new_status
            chat_session.save()
            
            serializer = ChatSessionSerializer(chat_session)
            return Response(serializer.data)
        else:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            
    except ChatSession.DoesNotExist:
        return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
