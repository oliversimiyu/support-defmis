from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.admin_profile, name='admin_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('admin-list/', views.admin_list, name='admin_list'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('edit-admin/<int:user_id>/', views.edit_admin, name='edit_admin'),
    path('delete-admin/<int:user_id>/', views.delete_admin, name='delete_admin'),
]