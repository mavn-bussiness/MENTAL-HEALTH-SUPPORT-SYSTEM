from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment, AppointmentFeedback, AppointmentCancellation, TherapistAvailability
from therapists.models import TherapistProfile
from django.core.exceptions import ValidationError


class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'therapist', 'appointment_date', 'appointment_type', 
            'duration_minutes', 'notes', 'is_online'
        ]
        widgets = {
            'appointment_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
            'therapist': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
            'appointment_type': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
            'duration_minutes': forms.Select(
                choices=[(30, '30 minutes'), (60, '60 minutes'), (90, '90 minutes')],
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                    'placeholder': 'Please describe what you would like to discuss or any specific concerns...'
                }
            ),
            'is_online': forms.CheckboxInput(
                attrs={
                    'class': 'rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show available therapists
        self.fields['therapist'].queryset = TherapistProfile.objects.filter(is_available=True)
        
        # Set minimum date to tomorrow
        min_date = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        self.fields['appointment_date'].widget.attrs['min'] = min_date
        
        # Set default duration
        self.fields['duration_minutes'].initial = 60
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        
        if not appointment_date:
            raise ValidationError("Please select an appointment date and time.")
        
        # Ensure appointment is at least 24 hours in the future
        if appointment_date <= timezone.now() + timedelta(hours=24):
            raise ValidationError("Appointments must be booked at least 24 hours in advance.")
        
        # Check if it's within business hours (9 AM - 6 PM)
        if appointment_date.hour < 9 or appointment_date.hour >= 18:
            raise ValidationError("Appointments can only be scheduled between 9:00 AM and 6:00 PM.")
        
        # Check if it's not on weekend (optional - remove if weekend appointments are allowed)
        if appointment_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            raise ValidationError("Appointments can only be scheduled on weekdays.")
        
        return appointment_date
    
    def clean(self):
        cleaned_data = super().clean()
        therapist = cleaned_data.get('therapist')
        appointment_date = cleaned_data.get('appointment_date')
        duration_minutes = cleaned_data.get('duration_minutes', 60)
        
        if therapist and appointment_date:
            # Check for conflicts with existing appointments
            end_time = appointment_date + timedelta(minutes=duration_minutes)
            conflicts = Appointment.objects.filter(
                therapist=therapist,
                status__in=['pending', 'confirmed'],
                appointment_date__lt=end_time,
                appointment_date__gt=appointment_date - timedelta(minutes=60)  # Assuming max 60min sessions
            )
            
            if self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            
            if conflicts.exists():
                raise ValidationError("This time slot is not available. Please choose a different time.")
        
        return cleaned_data


class AppointmentRescheduleForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'notes']
        widgets = {
            'appointment_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                    'placeholder': 'Any additional notes or changes to discuss...'
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to tomorrow
        min_date = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        self.fields['appointment_date'].widget.attrs['min'] = min_date
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        
        if appointment_date <= timezone.now() + timedelta(hours=24):
            raise ValidationError("Appointments must be rescheduled at least 24 hours in advance.")
        
        return appointment_date


class AppointmentCancellationForm(forms.ModelForm):
    class Meta:
        model = AppointmentCancellation
        fields = ['reason', 'detailed_reason']
        widgets = {
            'reason': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
            'detailed_reason': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                    'placeholder': 'Please provide additional details about the cancellation...'
                }
            ),
        }


class AppointmentFeedbackForm(forms.ModelForm):
    class Meta:
        model = AppointmentFeedback
        fields = ['rating', 'comment', 'would_recommend']
        widgets = {
            'rating': forms.RadioSelect(
                attrs={
                    'class': 'focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300'
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                    'placeholder': 'Please share your experience and any feedback...'
                }
            ),
            'would_recommend': forms.CheckboxInput(
                attrs={
                    'class': 'rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
        }


class TherapistNotesForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['therapist_notes', 'status']
        widgets = {
            'therapist_notes': forms.Textarea(
                attrs={
                    'rows': 6,
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                    'placeholder': 'Session notes, observations, and recommendations...'
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit status choices for therapists
        self.fields['status'].choices = [
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
            ('no_show', 'No Show'),
        ]


class AvailabilityFilterForm(forms.Form):
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }
        )
    )
    
    time_preference = forms.ChoiceField(
        choices=[
            ('', 'Any Time'),
            ('morning', 'Morning (9AM - 12PM)'),
            ('afternoon', 'Afternoon (12PM - 5PM)'),
            ('evening', 'Evening (5PM - 8PM)'),
        ],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }
        )
    )
    
    appointment_type = forms.ChoiceField(
        choices=[('', 'Any Type')] + Appointment.APPOINTMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }
        )
    )


class TherapistAvailabilityForm(forms.ModelForm):
    class Meta:
        model = TherapistAvailability
        fields = ['day_of_week', 'start_time', 'end_time', 'is_available']
        widgets = {
            'day_of_week': forms.Select(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
            'start_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
            'end_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
            'is_available': forms.CheckboxInput(
                attrs={
                    'class': 'rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                }
            ),
        }


# Quick booking form for dashboard
class QuickAppointmentForm(forms.Form):
    therapist = forms.ModelChoiceField(
        queryset=TherapistProfile.objects.filter(is_available=True),
        widget=forms.Select(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }
        )
    )
    
    preferred_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'min': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            }
        )
    )
    
    preferred_time = forms.ChoiceField(
        choices=[
            ('09:00', '9:00 AM'),
            ('10:00', '10:00 AM'),
            ('11:00', '11:00 AM'),
            ('14:00', '2:00 PM'),
            ('15:00', '3:00 PM'),
            ('16:00', '4:00 PM'),
            ('17:00', '5:00 PM'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }
        )
    )
    
    appointment_type = forms.ChoiceField(
        choices=Appointment.APPOINTMENT_TYPE_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
            }
        )
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Brief description of what you\'d like to discuss...'
            }
        )
    )