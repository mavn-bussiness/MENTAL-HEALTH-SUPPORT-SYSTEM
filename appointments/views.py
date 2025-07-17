from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentRequestForm
from therapists.models import TherapistProfile

def send_appointment_notification(appointment, action):
    # Placeholder for sending email notification to therapist
    pass

def create_appointment_reminders(appointment):
    # Placeholder for creating appointment reminders
    pass

@login_required
def request_appointment(request):
    """Request an appointment"""
    if request.user.role != 'client':
        messages.error(request, 'Access denied.')
        return redirect('accounts:landing')
    
    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            appointment.save()
            
            # Send email notification to therapist
            send_appointment_notification(appointment, 'requested')
            
            # Create reminders
            create_appointment_reminders(appointment)
            
            messages.success(request, 'Appointment request sent successfully!')
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentRequestForm()
    
    return render(request, 'appointments/request_appointment.html', {'form': form})
