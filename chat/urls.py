from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Public API endpoints (for widget)
    path('api/widget/config/', views.widget_config, name='widget_config'),
    path('api/chat/start/', views.start_chat, name='start_chat'),
    path('api/chat/<str:customer_id>/history/', views.chat_history, name='chat_history'),
    path('api/chat/message/', views.send_message, name='send_message'),
    
    # Admin API endpoints
    path('api/admin/sessions/', views.admin_chat_sessions, name='admin_chat_sessions'),
    path('api/admin/session/<uuid:session_id>/', views.admin_chat_detail, name='admin_chat_detail'),
    path('api/admin/session/<uuid:session_id>/status/', views.admin_update_chat_status, name='admin_update_chat_status'),
]