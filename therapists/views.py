from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import TherapistProfile
from .forms import TherapistProfileForm, TherapistAvailabilityForm
from appointments.models import Appointment
from django.utils import timezone

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

@login_required
def therapist_dashboard(request):
    """Therapist dashboard to view appointments"""
    if request.user.role != 'therapist':
        messages.error(request, 'Access denied. Therapists only.')
        return redirect('accounts:landing')
    
    therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
    upcoming_appointments = Appointment.objects.filter(
        therapist=therapist_profile,
        appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date')[:5]
    
    context = {
        'therapist': therapist_profile,
        'upcoming_appointments': upcoming_appointments,
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
            messages.success(request, 'Availability updated successfully!')
            return redirect('therapists:therapist_dashboard')
    else:
        form = TherapistAvailabilityForm(instance=therapist_profile)
    
    context = {'form': form, 'therapist': therapist_profile}
    return render(request, 'therapists/therapist_availability.html', context)