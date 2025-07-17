from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from .models import User
from .forms import ClientRegistrationForm, LoginForm, ProfileUpdateForm
from django.db.models import Q

def landing_page(request):
    """Landing page with login form"""
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('analytics:admin_dashboard')
        elif request.user.role == 'therapist':
            return redirect('therapists:therapist_dashboard')
        else:
            return redirect('accounts:client_dashboard')
    
    login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'accounts/landing.html', context)

def register_client(request):
    """Client registration view"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:landing')
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """Login view handling both username and email"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect('analytics:admin_dashboard')
            elif user.role == 'therapist':
                return redirect('therapists:therapist_dashboard')
            else:
                return redirect('accounts:client_dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def client_dashboard(request):
    """Client dashboard"""
    if request.user.role != 'client':
        messages.error(request, 'Access denied.')
        return redirect('accounts:landing')
    
    # Get user's assessment scores and appointments
    from assessments.models import AssessmentResult
    from appointments.models import Appointment
    from content.models import EducationalContent
    
    recent_assessments = AssessmentResult.objects.filter(user=request.user).order_by('-created_at')[:5]
    upcoming_appointments = Appointment.objects.filter(
        client=request.user, 
        status='confirmed'
    ).order_by('appointment_date')[:5]
    
    educational_content = EducationalContent.objects.filter(is_published=True).order_by('-created_at')[:5]
    
    context = {
        'recent_assessments': recent_assessments,
        'upcoming_appointments': upcoming_appointments,
        'educational_content': educational_content,
    }
    
    return render(request, 'accounts/client_dashboard.html', context)

@login_required
def profile_update(request):
    """Update client profile"""
    if request.user.role != 'client':
        messages.error(request, 'Access denied.')
        return redirect('accounts:landing')
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:client_dashboard')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_update.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('accounts:landing')
