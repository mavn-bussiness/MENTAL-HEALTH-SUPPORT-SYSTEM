from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    Appointment, AppointmentFeedback, AppointmentCancellation, 
    TherapistAvailability, AppointmentReminder
)
from .forms import (
    AppointmentBookingForm, AppointmentRescheduleForm, 
    AppointmentCancellationForm, AppointmentFeedbackForm,
    TherapistNotesForm, AvailabilityFilterForm, QuickAppointmentForm
)
from therapists.models import TherapistProfile


@login_required
def appointment_list(request):
    """List all appointments for the current user"""
    if request.user.role == 'client':
        appointments = Appointment.objects.filter(client=request.user)
    elif request.user.role == 'therapist':
        therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
        appointments = Appointment.objects.filter(therapist=therapist_profile)
    else:
        # Admin can see all appointments
        appointments = Appointment.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    # Filter by date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        appointments = appointments.filter(appointment_date__date__gte=date_from)
    if date_to:
        appointments = appointments.filter(appointment_date__date__lte=date_to)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        if request.user.role == 'client':
            appointments = appointments.filter(
                Q(therapist__user__first_name__icontains=search_query) |
                Q(therapist__user__last_name__icontains=search_query) |
                Q(therapist__specialization__icontains=search_query)
            )
        elif request.user.role == 'therapist':
            appointments = appointments.filter(
                Q(client__first_name__icontains=search_query) |
                Q(client__last_name__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
    
    # Order by appointment date
    appointments = appointments.order_by('-appointment_date')
    
    # Pagination
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get upcoming and past appointments counts
    upcoming_count = appointments.filter(
        appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).count()
    
    past_count = appointments.filter(
        appointment_date__lt=timezone.now()
    ).count()
    
    context = {
        'page_obj': page_obj,
        'appointments': page_obj,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
        'upcoming_count': upcoming_count,
        'past_count': past_count,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def book_appointment(request, therapist_id=None):
    """Book a new appointment"""
    if request.user.role != 'client':
        messages.error(request, 'Only clients can book appointments.')
        return redirect('accounts:landing')
    
    initial_data = {}
    if therapist_id:
        therapist = get_object_or_404(TherapistProfile, id=therapist_id, is_available=True)
        initial_data['therapist'] = therapist
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            appointment.save()
            
            # Send confirmation email to client
            send_appointment_confirmation_email(appointment)
            
            # Send notification to therapist
            send_therapist_notification_email(appointment)
            
            messages.success(
                request, 
                f'Appointment booked successfully with {appointment.therapist.user.get_full_name()} '
                f'on {appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p")}. '
                'You will receive a confirmation email shortly.'
            )
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentBookingForm(initial=initial_data, user=request.user)
    
    therapists = TherapistProfile.objects.filter(is_available=True)
    context = {
        'form': form,
        'therapists': therapists,
        'therapist_id': therapist_id,
    }
    return render(request, 'appointments/book_appointment.html', context)

@login_required
def appointment_booking_success(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    return render(request, 'appointments/appointment_booking_success.html', {'appointment': appointment})

@login_required
def appointment_detail(request, appointment_id):
    """View appointment details"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user.role == 'client' and appointment.client != request.user:
        messages.error(request, 'You can only view your own appointments.')
        return redirect('appointments:appointment_list')
    elif request.user.role == 'therapist':
        therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
        if appointment.therapist != therapist_profile:
            messages.error(request, 'You can only view your own appointments.')
            return redirect('appointments:appointment_list')
    
    context = {
        'appointment': appointment,
        'can_cancel': appointment.can_be_cancelled,
        'can_reschedule': appointment.can_be_rescheduled,
    }
    
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule an existing appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user.role == 'client' and appointment.client != request.user:
        messages.error(request, 'You can only reschedule your own appointments.')
        return redirect('appointments:appointment_list')
    elif request.user.role == 'therapist':
        therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
        if appointment.therapist != therapist_profile:
            messages.error(request, 'You can only reschedule your own appointments.')
            return redirect('appointments:appointment_list')
    
    if not appointment.can_be_rescheduled:
        messages.error(request, 'This appointment cannot be rescheduled.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    if request.method == 'POST':
        form = AppointmentRescheduleForm(request.POST, instance=appointment)
        if form.is_valid():
            old_date = appointment.appointment_date
            appointment = form.save()
            
            # Send reschedule notification emails
            send_reschedule_notification_email(appointment, old_date)
            
            messages.success(
                request,
                f'Appointment rescheduled successfully to {appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p")}.'
            )
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    else:
        form = AppointmentRescheduleForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/reschedule_appointment.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user.role == 'client' and appointment.client != request.user:
        messages.error(request, 'You can only cancel your own appointments.')
        return redirect('appointments:appointment_list')
    elif request.user.role == 'therapist':
        therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
        if appointment.therapist != therapist_profile:
            messages.error(request, 'You can only cancel your own appointments.')
            return redirect('appointments:appointment_list')
    
    if not appointment.can_be_cancelled:
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    if request.method == 'POST':
        form = AppointmentCancellationForm(request.POST)
        if form.is_valid():
            # Create cancellation record
            cancellation = form.save(commit=False)
            cancellation.appointment = appointment
            cancellation.cancelled_by = request.user
            cancellation.save()
            
            # Update appointment status
            appointment.status = 'cancelled'
            appointment.cancelled_at = timezone.now()
            appointment.cancelled_by = request.user
            appointment.cancellation_reason = form.cleaned_data['detailed_reason']
            appointment.save()
            
            # Send cancellation notification emails
            send_cancellation_notification_email(appointment, cancellation)
            
            messages.success(request, 'Appointment cancelled successfully.')
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentCancellationForm()
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/cancel_appointment.html', context)


@login_required
def appointment_feedback(request, appointment_id):
    """Submit feedback for completed appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Only clients can leave feedback and only for their own completed appointments
    if request.user.role != 'client' or appointment.client != request.user:
        messages.error(request, 'You can only provide feedback for your own appointments.')
        return redirect('appointments:appointment_list')
    
    if appointment.status != 'completed':
        messages.error(request, 'You can only provide feedback for completed appointments.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    # Check if feedback already exists
    try:
        existing_feedback = appointment.feedback
        messages.info(request, 'You have already provided feedback for this appointment.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    except AppointmentFeedback.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = AppointmentFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.appointment = appointment
            feedback.save()
            
            messages.success(request, 'Thank you for your feedback!')
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    else:
        form = AppointmentFeedbackForm()
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_feedback.html', context)


@login_required
def therapist_notes(request, appointment_id):
    """Add or update therapist notes for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Only therapists can add notes to their own appointments
    if request.user.role != 'therapist':
        messages.error(request, 'Only therapists can add session notes.')
        return redirect('appointments:appointment_list')
    
    therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
    if appointment.therapist != therapist_profile:
        messages.error(request, 'You can only add notes to your own appointments.')
        return redirect('appointments:appointment_list')
    
    if request.method == 'POST':
        form = TherapistNotesForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session notes updated successfully.')
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    else:
        form = TherapistNotesForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/therapist_notes.html', context)


@login_required
def quick_appointment(request):
    """Quick appointment booking from dashboard"""
    if request.user.role != 'client':
        messages.error(request, 'Only clients can book appointments.')
        return redirect('accounts:landing')
    
    if request.method == 'POST':
        form = QuickAppointmentForm(request.POST)
        if form.is_valid():
            # Combine date and time
            preferred_date = form.cleaned_data['preferred_date']
            preferred_time = datetime.strptime(form.cleaned_data['preferred_time'], '%H:%M').time()
            appointment_datetime = datetime.combine(preferred_date, preferred_time)
            appointment_datetime = timezone.make_aware(appointment_datetime)
            
            # Check if the slot is available
            conflicts = Appointment.objects.filter(
                therapist=form.cleaned_data['therapist'],
                appointment_date=appointment_datetime,
                status__in=['pending', 'confirmed']
            )
            
            if conflicts.exists():
                messages.error(request, 'The selected time slot is not available. Please choose a different time.')
            else:
                # Create the appointment
                appointment = Appointment.objects.create(
                    client=request.user,
                    therapist=form.cleaned_data['therapist'],
                    appointment_date=appointment_datetime,
                    appointment_type=form.cleaned_data['appointment_type'],
                    notes=form.cleaned_data['notes'],
                    status='pending'
                )
                
                # Send confirmation emails
                send_appointment_confirmation_email(appointment)
                send_therapist_notification_email(appointment)
                
                messages.success(request, 'Quick appointment booked successfully!')
                return redirect('appointments:appointment_list')
    else:
        form = QuickAppointmentForm()
    
    context = {'form': form}
    return render(request, 'appointments/quick_appointment.html', context)


@login_required
def therapist_availability(request):
    """Manage therapist availability"""
    if request.user.role != 'therapist':
        messages.error(request, 'Only therapists can manage availability.')
        return redirect('accounts:landing')
    
    therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
    availability_schedule = TherapistAvailability.objects.filter(
        therapist=therapist_profile
    ).order_by('day_of_week', 'start_time')
    
    context = {
        'availability_schedule': availability_schedule,
        'therapist_profile': therapist_profile,
    }
    return render(request, 'therapists/therapist_availability.html', context)


@login_required
def upcoming_appointments(request):
    """View upcoming appointments"""
    if request.user.role == 'client':
        appointments = Appointment.objects.filter(
            client=request.user,
            appointment_date__gte=timezone.now(),
            status__in=['pending', 'confirmed']
        ).order_by('appointment_date')
    elif request.user.role == 'therapist':
        therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
        appointments = Appointment.objects.filter(
            therapist=therapist_profile,
            appointment_date__gte=timezone.now(),
            status__in=['pending', 'confirmed']
        ).order_by('appointment_date')
    else:
        appointments = Appointment.objects.filter(
            appointment_date__gte=timezone.now(),
            status__in=['pending', 'confirmed']
        ).order_by('appointment_date')
    
    context = {
        'appointments': appointments,
        'today': timezone.now().date(),
    }
    return render(request, 'appointments/upcoming_appointments.html', context)


@login_required
def past_appointments(request):
    """View past appointments"""
    if request.user.role == 'client':
        appointments = Appointment.objects.filter(
            client=request.user,
            appointment_date__lt=timezone.now()
        ).order_by('-appointment_date')
    elif request.user.role == 'therapist':
        therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
        appointments = Appointment.objects.filter(
            therapist=therapist_profile,
            appointment_date__lt=timezone.now()
        ).order_by('-appointment_date')
    else:
        appointments = Appointment.objects.filter(
            appointment_date__lt=timezone.now()
        ).order_by('-appointment_date')
    
    # Pagination
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'appointments': page_obj,
    }
    return render(request, 'appointments/past_appointments.html', context)


@login_required
@require_http_methods(["POST"])
def confirm_appointment(request, appointment_id):
    """Confirm an appointment (therapist only)"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user.role != 'therapist':
        return JsonResponse({'success': False, 'error': 'Only therapists can confirm appointments.'})
    
    therapist_profile = get_object_or_404(TherapistProfile, user=request.user)
    if appointment.therapist != therapist_profile:
        return JsonResponse({'success': False, 'error': 'You can only confirm your own appointments.'})
    
    if appointment.status != 'pending':
        return JsonResponse({'success': False, 'error': 'Only pending appointments can be confirmed.'})
    
    appointment.status = 'confirmed'
    appointment.confirmed_at = timezone.now()
    appointment.save()
    
    # Send confirmation email to client
    send_appointment_confirmed_email(appointment)
    
    return JsonResponse({'success': True, 'message': 'Appointment confirmed successfully.'})


@login_required
def check_availability(request):
    """AJAX endpoint to check therapist availability"""
    therapist_id = request.GET.get('therapist_id')
    date = request.GET.get('date')
    
    if not therapist_id or not date:
        return JsonResponse({'available_slots': []})
    
    try:
        therapist = TherapistProfile.objects.get(id=therapist_id, is_available=True)
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get therapist's availability for the day
        day_of_week = date_obj.weekday()
        availability = TherapistAvailability.objects.filter(
            therapist=therapist,
            day_of_week=day_of_week,
            is_available=True
        )
        
        available_slots = []
        for avail in availability:
            # Generate hourly slots between start and end time
            current_time = datetime.combine(date_obj, avail.start_time)
            end_time = datetime.combine(date_obj, avail.end_time)
            
            while current_time < end_time:
                slot_datetime = timezone.make_aware(current_time)
                
                # Check if slot is not already booked
                conflicts = Appointment.objects.filter(
                    therapist=therapist,
                    appointment_date=slot_datetime,
                    status__in=['pending', 'confirmed']
                )
                
                if not conflicts.exists() and slot_datetime > timezone.now():
                    available_slots.append({
                        'time': current_time.strftime('%H:%M'),
                        'display': current_time.strftime('%I:%M %p')
                    })
                
                current_time += timedelta(hours=1)
        
        return JsonResponse({'available_slots': available_slots})
    
    except (TherapistProfile.DoesNotExist, ValueError):
        return JsonResponse({'available_slots': []})


# Email notification functions
def send_appointment_confirmation_email(appointment):
    """Send appointment confirmation email to client"""
    subject = f'Appointment Confirmation - {appointment.appointment_date.strftime("%B %d, %Y")}'
    message = f'''
    Dear {appointment.client.get_full_name()},

    Your appointment has been successfully booked with {appointment.therapist.user.get_full_name()}.

    Appointment Details:
    - Date: {appointment.appointment_date.strftime("%B %d, %Y")}
    - Time: {appointment.appointment_date.strftime("%I:%M %p")}
    - Type: {appointment.get_appointment_type_display()}
    - Duration: {appointment.duration_minutes} minutes
    - Location: {'Online' if appointment.is_online else appointment.location or 'TBD'}

    Please arrive 5 minutes early for your appointment.

    Best regards,
    Mental Health Support Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.client.email],
        fail_silently=True,
    )


def send_therapist_notification_email(appointment):
    """Send new appointment notification to therapist"""
    subject = f'New Appointment Booking - {appointment.appointment_date.strftime("%B %d, %Y")}'
    message = f'''
    Dear {appointment.therapist.user.get_full_name()},

    A new appointment has been booked with you.

    Appointment Details:
    - Client: {appointment.client.get_full_name()}
    - Date: {appointment.appointment_date.strftime("%B %d, %Y")}
    - Time: {appointment.appointment_date.strftime("%I:%M %p")}
    - Type: {appointment.get_appointment_type_display()}
    - Duration: {appointment.duration_minutes} minutes
    - Notes: {appointment.notes or 'None'}

    Please log in to your dashboard to confirm or manage this appointment.

    Best regards,
    Mental Health Support Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.therapist.user.email],
        fail_silently=True,
    )


def send_appointment_confirmed_email(appointment):
    """Send appointment confirmation email to client"""
    subject = f'Appointment Confirmed - {appointment.appointment_date.strftime("%B %d, %Y")}'
    message = f'''
    Dear {appointment.client.get_full_name()},

    Your appointment with {appointment.therapist.user.get_full_name()} has been confirmed.

    Appointment Details:
    - Date: {appointment.appointment_date.strftime("%B %d, %Y")}
    - Time: {appointment.appointment_date.strftime("%I:%M %p")}
    - Type: {appointment.get_appointment_type_display()}
    - Duration: {appointment.duration_minutes} minutes

    We look forward to seeing you at your appointment.

    Best regards,
    Mental Health Support Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.client.email],
        fail_silently=True,
    )


def send_reschedule_notification_email(appointment, old_date):
    """Send reschedule notification emails"""
    # Email to client
    subject = f'Appointment Rescheduled - {appointment.appointment_date.strftime("%B %d, %Y")}'
    message = f'''
    Dear {appointment.client.get_full_name()},

    Your appointment has been rescheduled.

    Previous Date/Time: {old_date.strftime("%B %d, %Y at %I:%M %p")}
    New Date/Time: {appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p")}

    Therapist: {appointment.therapist.user.get_full_name()}

    Best regards,
    Mental Health Support Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.client.email],
        fail_silently=True,
    )
    
    # Email to therapist
    send_mail(
        subject,
        message.replace(appointment.client.get_full_name(), appointment.therapist.user.get_full_name()).replace(
            'Your appointment', f'The appointment with {appointment.client.get_full_name()}'
        ),
        settings.DEFAULT_FROM_EMAIL,
        [appointment.therapist.user.email],
        fail_silently=True,
    )


def send_cancellation_notification_email(appointment, cancellation):
    """Send cancellation notification emails"""
    subject = f'Appointment Cancelled - {appointment.appointment_date.strftime("%B %d, %Y")}'
    
    # Email to both parties
    recipients = [appointment.client.email, appointment.therapist.user.email]
    
    message = f'''
    Dear User,

    The appointment scheduled for {appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p")} has been cancelled.

    Cancellation Details:
    - Cancelled by: {cancellation.cancelled_by.get_full_name()}
    - Reason: {cancellation.get_reason_display()}
    - Additional details: {cancellation.detailed_reason or 'None provided'}

    Best regards,
    Mental Health Support Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=True,
    )