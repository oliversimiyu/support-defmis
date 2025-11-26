from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from .forms import AdminProfileForm, CustomPasswordChangeForm, CreateAdminForm


def is_staff_user(user):
    """Check if user is staff"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def admin_profile(request):
    """View for admin to update their profile"""
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:admin_profile')
    else:
        form = AdminProfileForm(instance=request.user, user=request.user)
    
    return render(request, 'accounts/admin_profile.html', {'form': form})


@login_required
@user_passes_test(is_staff_user)
def change_password(request):
    """View for admin to change their password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important for keeping user logged in
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('accounts:admin_profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
@user_passes_test(is_staff_user)
def admin_list(request):
    """View to list all admin users"""
    admin_users = User.objects.filter(is_staff=True).order_by('username')
    
    # Pagination
    paginator = Paginator(admin_users, 10)  # Show 10 admins per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin_list.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_staff_user)
def create_admin(request):
    """View for creating new admin accounts"""
    if request.method == 'POST':
        form = CreateAdminForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Admin account "{user.username}" has been created successfully.')
            return redirect('accounts:admin_list')
    else:
        form = CreateAdminForm()
    
    return render(request, 'accounts/create_admin.html', {'form': form})


@login_required
@user_passes_test(is_staff_user)
def edit_admin(request, user_id):
    """View for editing admin accounts (only for superusers)"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit other admin accounts.')
        return redirect('accounts:admin_list')
    
    admin_user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=admin_user, user=admin_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Admin account "{admin_user.username}" has been updated successfully.')
            return redirect('accounts:admin_list')
    else:
        form = AdminProfileForm(instance=admin_user, user=admin_user)
    
    return render(request, 'accounts/edit_admin.html', {'form': form, 'admin_user': admin_user})


@login_required
@user_passes_test(is_staff_user)
def delete_admin(request, user_id):
    """View for deleting admin accounts (only for superusers)"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete admin accounts.')
        return redirect('accounts:admin_list')
    
    admin_user = get_object_or_404(User, id=user_id, is_staff=True)
    
    # Prevent deleting self
    if admin_user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:admin_list')
    
    if request.method == 'POST':
        username = admin_user.username
        admin_user.delete()
        messages.success(request, f'Admin account "{username}" has been deleted successfully.')
        return redirect('accounts:admin_list')
    
    return render(request, 'accounts/delete_admin.html', {'admin_user': admin_user})
