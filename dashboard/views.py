from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Q
from chat.models import ChatSession, Message
from django.utils import timezone
from datetime import timedelta


@login_required(login_url='dashboard:login')
def dashboard_home(request):
    if not request.user.is_staff:
        messages.error(request, 'You need staff privileges to access the dashboard.')
        return redirect('dashboard:login')
    """Admin dashboard home page with statistics"""
    # Get statistics
    total_sessions = ChatSession.objects.count()
    open_sessions = ChatSession.objects.filter(status='open').count()
    closed_sessions = ChatSession.objects.filter(status='closed').count()
    unread_messages = Message.objects.filter(sender_type='customer', is_read=False).count()
    
    # Get recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_sessions = ChatSession.objects.filter(created_at__gte=week_ago).count()
    
    # Get recent conversations
    recent_conversations = ChatSession.objects.select_related().prefetch_related('messages')[:10]
    
    context = {
        'total_sessions': total_sessions,
        'open_sessions': open_sessions,
        'closed_sessions': closed_sessions,
        'unread_messages': unread_messages,
        'recent_sessions': recent_sessions,
        'recent_conversations': recent_conversations,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required(login_url='dashboard:login')
def conversations_list(request):
    if not request.user.is_staff:
        messages.error(request, 'You need staff privileges to access the dashboard.')
        return redirect('dashboard:login')
    """List all conversations with filtering"""
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    conversations = ChatSession.objects.all().order_by('-updated_at')
    
    if status_filter != 'all':
        conversations = conversations.filter(status=status_filter)
    
    if search_query:
        conversations = conversations.filter(
            Q(customer_name__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(customer_id__icontains=search_query)
        )
    
    context = {
        'conversations': conversations,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/conversations.html', context)


@login_required(login_url='dashboard:login')
def conversation_detail(request, session_id):
    if not request.user.is_staff:
        messages.error(request, 'You need staff privileges to access the dashboard.')
        return redirect('dashboard:login')
    """Detailed view of a single conversation"""
    try:
        conversation = ChatSession.objects.get(id=session_id)
        messages = conversation.messages.all().order_by('timestamp')
        
        # Mark customer messages as read
        Message.objects.filter(
            chat_session=conversation,
            sender_type='customer',
            is_read=False
        ).update(is_read=True)
        
        context = {
            'conversation': conversation,
            'messages': messages,
        }
        
        return render(request, 'dashboard/conversation_detail.html', context)
    except ChatSession.DoesNotExist:
        return redirect('dashboard:conversations')


@login_required(login_url='dashboard:login')
def widget_settings(request):
    if not request.user.is_staff:
        messages.error(request, 'You need staff privileges to access the dashboard.')
        return redirect('dashboard:login')
    """Chat widget configuration settings"""
    from chat.models import ChatWidget
    
    widget, created = ChatWidget.objects.get_or_create(
        defaults={
            'name': 'Support Chat',
            'welcome_message': 'Hi there! How can we help you today?',
            'primary_color': '#007bff',
            'widget_position': 'bottom-right',
            'is_active': True
        }
    )
    
    if request.method == 'POST':
        widget.name = request.POST.get('name', widget.name)
        widget.welcome_message = request.POST.get('welcome_message', widget.welcome_message)
        widget.primary_color = request.POST.get('primary_color', widget.primary_color)
        widget.widget_position = request.POST.get('widget_position', widget.widget_position)
        widget.is_active = request.POST.get('is_active') == 'on'
        widget.save()
        
        return redirect('dashboard:widget_settings')
    
    context = {
        'widget': widget,
    }
    
    return render(request, 'dashboard/widget_settings.html', context)


def dashboard_login(request):
    """Custom login page for dashboard"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid credentials or insufficient permissions.')
        else:
            messages.error(request, 'Please enter both username and password.')
    
    return render(request, 'dashboard/login.html')


def dashboard_logout(request):
    """Custom logout for dashboard"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('dashboard:login')
