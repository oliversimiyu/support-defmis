from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    path('conversations/', views.conversations_list, name='conversations'),
    path('conversation/<uuid:session_id>/', views.conversation_detail, name='conversation_detail'),
    path('settings/widget/', views.widget_settings, name='widget_settings'),
]