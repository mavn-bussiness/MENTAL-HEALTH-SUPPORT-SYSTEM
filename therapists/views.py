from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import TherapistProfile
from .forms import TherapistProfileForm, TherapistAvailabilityForm
from appointments.models import Appointment
from django.utils import timezone
from datetime import timedelta
from .models import TherapistProfile, ActivityLog

def therapist_directory(request):
    """List all available therapists with search and filter"""
    therapists = TherapistProfile.objects.filter(is_available=True)
    
    # Search and filter
    search_query = request.GET.get('search', '')
    specialization = request.GET.get('specialization', '')
    location = request.GET.get('location', '')
    
    if search_query:
        therapists = therapists.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(bio__icontains=search_query)
        )
    if specialization:
        therapists = therapists.filter(specialization=specialization)
    if location:
        therapists = therapists.filter(location__icontains=location)
    
    context = {
        'therapists': therapists,
        'specializations': TherapistProfile.SPECIALIZATION_CHOICES,
        'search_query': search_query,
        'selected_specialization': specialization,
        'selected_location': location,
    }
    return render(request, 'therapists/therapist_directory.html', context)

def therapist_detail(request, pk):
    """Display details of a specific therapist"""
    therapist = get_object_or_404(TherapistProfile, pk=pk, is_available=True)
    context = {'therapist': therapist}
    return render(request, 'therapists/therapist_detail.html', context)

def therapist_dashboard(request):
    """Enhanced Therapist dashboard with dynamic statistics and activity"""
    if request.user.role != 'therapist':
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('accounts:landing')
    
    therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
    now = timezone.now()
    today = now.date()
    
    # Dynamic Statistics
    upcoming_appointments = Appointment.objects.filter(
        therapist=therapist_profile,
        appointment_date__gte=now,
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date')[:5]
    
    # Today's appointments count
    todays_appointments = Appointment.objects.filter(
        therapist=therapist_profile,
        appointment_date__date=today,
        status__in=['pending', 'confirmed', 'completed']
    ).count()
    
    # Total unique patients
    total_patients = Appointment.objects.filter(
        therapist=therapist_profile
    ).values('client').distinct().count()
    
    # Unread messages count (you'll need to adapt this based on your messaging model)
    # For now, using a placeholder - replace with your actual message model
    unread_messages = 0  # Replace with actual query when you have messaging system
    
    # Profile views (you can track this with a separate model or analytics)
    profile_views = 0  # Placeholder - implement tracking if needed
    
    # Recent Activity - Dynamic based on actual data
    recent_activities = []
    
    # Get recent appointments for activity
    recent_appointments = Appointment.objects.filter(
        therapist=therapist_profile,
        created_at__gte=now - timedelta(days=7)
    ).order_by('-created_at')[:10]
    
    for appointment in recent_appointments:
        activity_data = {
            'type': 'appointment',
            'icon_class': 'text-blue-600',
            'bg_class': 'bg-blue-50',
            'created_at': appointment.created_at,
        }
        
        if appointment.status == 'pending':
            activity_data.update({
                'title': 'New appointment request',
                'description': f'From {appointment.client.first_name} {appointment.client.last_name}',
                'icon': 'plus'
            })
        elif appointment.status == 'confirmed':
            activity_data.update({
                'title': 'Appointment confirmed',
                'description': f'With {appointment.client.first_name} {appointment.client.last_name}',
                'icon': 'check',
                'icon_class': 'text-green-600',
                'bg_class': 'bg-green-50'
            })
        elif appointment.status == 'completed':
            activity_data.update({
                'title': 'Session completed',
                'description': f'With {appointment.client.first_name} {appointment.client.last_name}',
                'icon': 'check-circle',
                'icon_class': 'text-green-600',
                'bg_class': 'bg-green-50'
            })
        elif appointment.status == 'cancelled':
            activity_data.update({
                'title': 'Appointment cancelled',
                'description': f'By {appointment.client.first_name} {appointment.client.last_name}',
                'icon': 'x-circle',
                'icon_class': 'text-red-600',
                'bg_class': 'bg-red-50'
            })
        
        recent_activities.append(activity_data)
    
    # Add profile update activity if recently updated
    if therapist_profile.updated_at >= now - timedelta(days=7):
        recent_activities.append({
            'type': 'profile',
            'title': 'Profile updated',
            'description': 'Your profile information was updated',
            'created_at': therapist_profile.updated_at,
            'icon': 'user',
            'icon_class': 'text-purple-600',
            'bg_class': 'bg-purple-50'
        })
    
    # Sort activities by date (most recent first)
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)
    recent_activities = recent_activities[:5]  # Limit to 5 most recent
    
    # Weekly statistics for trends
    week_ago = now - timedelta(days=7)
    weekly_appointments = Appointment.objects.filter(
        therapist=therapist_profile,
        created_at__gte=week_ago
    ).count()
    
    weekly_completed = Appointment.objects.filter(
        therapist=therapist_profile,
        status='completed',
        appointment_date__gte=week_ago
    ).count()
    
    context = {
        'therapist': therapist_profile,
        'upcoming_appointments': upcoming_appointments,
        'todays_appointments': todays_appointments,
        'total_patients': total_patients,
        'unread_messages': unread_messages,
        'profile_views': profile_views,
        'recent_activities': recent_activities,
        'weekly_appointments': weekly_appointments,
        'weekly_completed': weekly_completed,
    }
    return render(request, 'therapists/therapist_dashboard.html', context)
    

@login_required
def therapist_profile_edit(request):
    """Allow therapists to edit their profile"""
    if request.user.role != 'therapist':
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('accounts:landing')
    
    therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
    if request.method == 'POST':
        form = TherapistProfileForm(request.POST, instance=therapist_profile)
        if form.is_valid():
            form.save()
            
            # Log the profile update activity
            create_activity_log(
                therapist=therapist_profile,
                activity_type='profile_updated',
                description='Profile information updated'
            )
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('therapists:therapist_dashboard')
    else:
        form = TherapistProfileForm(instance=therapist_profile)
    
    context = {'form': form, 'therapist': therapist_profile}
    return render(request, 'therapists/therapist_profile_edit.html', context)

@login_required
def therapist_availability(request):
    """Allow therapists to manage their availability"""
    if request.user.role != 'therapist':
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('accounts:landing')
    
    therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
    if request.method == 'POST':
        form = TherapistAvailabilityForm(request.POST, instance=therapist_profile)
        if form.is_valid():
            form.save()
            
            # Log the availability update activity
            create_activity_log(
                therapist=therapist_profile,
                activity_type='availability_updated',
                description='Availability schedule updated'
            )
            
            messages.success(request, 'Availability updated successfully!')
            return redirect('therapists:therapist_dashboard')
    else:
        form = TherapistAvailabilityForm(instance=therapist_profile)
    
    context = {'form': form, 'therapist': therapist_profile}
    return render(request, 'therapists/therapist_availability.html', context)

def create_activity_log(therapist, activity_type, description, related_client=None, related_appointment=None):
    """Helper function to create activity logs"""
    try:
        ActivityLog.objects.create(
            therapist=therapist,
            activity_type=activity_type,
            description=description,
            related_client=related_client,
            related_appointment=related_appointment
        )
    except Exception as e:
        # Log the error but don't break the main functionality
        pass