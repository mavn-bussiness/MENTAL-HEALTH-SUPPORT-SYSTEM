from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

User = get_user_model()

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Initial Consultation'),
        ('therapy', 'Therapy Session'),
        ('follow_up', 'Follow-up Session'),
        ('assessment', 'Assessment Session'),
        ('emergency', 'Emergency Session'),
    ]
    
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_appointments',
        limit_choices_to={'role': 'client'}
    )
    therapist = models.ForeignKey(
        'therapists.TherapistProfile', 
        on_delete=models.CASCADE, 
        related_name='therapist_appointments'
    )
    appointment_date = models.DateTimeField()
    appointment_type = models.CharField(
        max_length=20, 
        choices=APPOINTMENT_TYPE_CHOICES, 
        default='consultation'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    duration_minutes = models.PositiveIntegerField(default=60)
    notes = models.TextField(blank=True, help_text="Client's initial notes or concerns")
    therapist_notes = models.TextField(blank=True, help_text="Therapist's session notes")
    location = models.CharField(max_length=255, blank=True, help_text="Meeting location or platform")
    is_online = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True, help_text="Video call link for online sessions")
    
    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='cancelled_appointments'
    )
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-appointment_date']
        indexes = [
            models.Index(fields=['client', 'appointment_date']),
            models.Index(fields=['therapist', 'appointment_date']),
            models.Index(fields=['status', 'appointment_date']),
        ]
    
    def __str__(self):
        return f"{self.client.get_full_name()} with {self.therapist.user.get_full_name()} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"
    
    def clean(self):
        # Validate appointment is in the future
        if self.appointment_date <= timezone.now():
            raise ValidationError("Appointment must be scheduled for a future date and time.")
        
        # Check for conflicting appointments
        if self.pk:  # If updating existing appointment
            conflicting_appointments = Appointment.objects.filter(
                therapist=self.therapist,
                appointment_date__range=(
                    self.appointment_date - timedelta(minutes=self.duration_minutes),
                    self.appointment_date + timedelta(minutes=self.duration_minutes)
                ),
                status__in=['confirmed', 'pending']
            ).exclude(pk=self.pk)
        else:  # If creating new appointment
            conflicting_appointments = Appointment.objects.filter(
                therapist=self.therapist,
                appointment_date__range=(
                    self.appointment_date - timedelta(minutes=self.duration_minutes),
                    self.appointment_date + timedelta(minutes=self.duration_minutes)
                ),
                status__in=['confirmed', 'pending']
            )
        
        if conflicting_appointments.exists():
            raise ValidationError("This time slot conflicts with another appointment.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        
        # Set confirmed_at when status changes to confirmed
        if self.status == 'confirmed' and not self.confirmed_at:
            self.confirmed_at = timezone.now()
        
        # Set cancelled_at when status changes to cancelled
        if self.status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_upcoming(self):
        return self.appointment_date > timezone.now() and self.status in ['pending', 'confirmed']
    
    @property
    def is_past(self):
        return self.appointment_date < timezone.now()
    
    @property
    def can_be_cancelled(self):
        # Can cancel if appointment is more than 24 hours away
        return (
            self.appointment_date > timezone.now() + timedelta(hours=24) and 
            self.status in ['pending', 'confirmed']
        )
    
    @property
    def can_be_rescheduled(self):
        return self.status in ['pending', 'confirmed'] and not self.is_past
    
    def get_end_time(self):
        return self.appointment_date + timedelta(minutes=self.duration_minutes)


class TherapistAvailability(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    therapist = models.ForeignKey(
        'therapists.TherapistProfile', 
        on_delete=models.CASCADE, 
        related_name='availability_schedule'
    )
    day_of_week = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['therapist', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.therapist.user.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")


class AppointmentReminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='reminders'
    )
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPE_CHOICES)
    scheduled_time = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"Reminder for {self.appointment} - {self.get_reminder_type_display()}"


class AppointmentFeedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='feedback'
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    would_recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.appointment} - {self.rating}/5"


class AppointmentCancellation(models.Model):
    CANCELLATION_REASON_CHOICES = [
        ('emergency', 'Emergency'),
        ('illness', 'Illness'),
        ('schedule_conflict', 'Schedule Conflict'),
        ('personal', 'Personal Reasons'),
        ('no_longer_needed', 'No Longer Needed'),
        ('other', 'Other'),
    ]
    
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='cancellation_details'
    )
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=CANCELLATION_REASON_CHOICES)
    detailed_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(auto_now_add=True)
    refund_issued = models.BooleanField(default=False)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Cancellation of {self.appointment} by {self.cancelled_by.get_full_name()}"