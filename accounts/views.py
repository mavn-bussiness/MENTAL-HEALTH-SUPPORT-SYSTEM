from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from .models import User
from .forms import ClientRegistrationForm, LoginForm, ProfileUpdateForm, PasswordResetForm
from content.models import EducationalContent
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from assessments.models import AssessmentResponse
from appointments.models import Appointment
import logging

# Set up logging
logger = logging.getLogger(__name__)

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
    return render(request, 'accounts/login.html', context)


def register_client(request):
    """Handle client registration with proper error handling"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST, request.FILES)
        
        # Log form submission for debugging
        logger.info(f"Registration form submitted with data: {request.POST.keys()}")
        
        if form.is_valid():
            try:
                # Save the user
                user = form.save()
                logger.info(f"User created successfully: {user.email}")
                
                # Handle AJAX request
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Registration successful! Please login.'
                    })
                
                # Handle regular form submission
                messages.success(request, 'Registration successful! Please login.')
                return redirect('accounts:landing')
                
            except Exception as e:
                logger.error(f"Error saving user: {str(e)}")
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'errors': ['An error occurred while creating your account. Please try again.']
                    }, status=500)
                
                messages.error(request, 'An error occurred while creating your account. Please try again.')
        
        else:
            # Log form errors for debugging
            logger.warning(f"Form validation failed: {form.errors}")
            
            # Handle AJAX request with form errors
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = []
                for field, msgs in form.errors.items():
                    field_name = form.fields[field].label if field in form.fields else field.replace('_', ' ').title()
                    for msg in msgs:
                        errors.append(f"{field_name}: {msg}")
                
                return JsonResponse({
                    'success': False, 
                    'errors': errors
                }, status=400)
            
            # Handle regular form submission
            for field, msgs in form.errors.items():
                for msg in msgs:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {msg}")
    
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
            if user.role == 'admin':
                return redirect('analytics:admin_dashboard')
            elif user.role == 'therapist':
                return redirect('therapists:therapist_dashboard')
            else:
                return redirect('accounts:client_dashboard')
        else:
            # Handle login errors
            for field, msgs in form.errors.items():
                for msg in msgs:
                    messages.error(request, msg)
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def client_dashboard(request):
    """Client dashboard"""
    if request.user.role != 'client':
        messages.error(request, 'Access denied.')
        return redirect('accounts:landing')
    
    # Fetch recent assessments (last 5, ordered by completion date)
    recent_assessments = AssessmentResponse.objects.filter(user=request.user).order_by('-completed_at')[:5]
    
    # Fetch upcoming appointments (pending or confirmed, ordered by date)
    upcoming_appointments = Appointment.objects.filter(
        client=request.user,
        appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date')[:5]
    
    # Fetch recommended educational content
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
            return redirect('accounts:profile_update_success')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_update.html', {'form': form})

@login_required
def profile_update_success(request):
    """Display confirmation after successful profile update"""
    if request.user.role != 'client':
        messages.error(request, 'Access denied.')
        return redirect('accounts:landing')
    
    return render(request, 'accounts/profile_update_success.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('accounts:landing')

def password_reset_request(request):
    """Handle password reset request"""
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(
                reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Password reset link sent to your email.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'No user found with this email.')
    return render(request, 'accounts/password_reset_request.html')

def password_reset_confirm(request, uidb64, token):
    """Handle password reset confirmation"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, 'Password reset successfully! Please login.')
                return redirect('accounts:login')
        else:
            form = PasswordResetForm()
        return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'validlink': True})
    else:
        return render(request, 'accounts/password_reset_confirm.html', {'validlink': False})