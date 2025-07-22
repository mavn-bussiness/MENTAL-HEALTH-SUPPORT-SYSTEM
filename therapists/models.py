from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class TherapistProfile(models.Model):
    SPECIALIZATION_CHOICES = [
        ('anxiety', 'Anxiety Disorders'),
        ('depression', 'Depression'),
        ('trauma', 'Trauma & PTSD'),
        ('relationships', 'Relationship Counseling'),
        ('addiction', 'Addiction Recovery'),
        ('grief', 'Grief & Loss'),
        ('eating_disorders', 'Eating Disorders'),
        ('bipolar', 'Bipolar Disorder'),
        ('ocd', 'OCD'),
        ('adhd', 'ADHD'),
        ('family_therapy', 'Family Therapy'),
        ('child_therapy', 'Child & Adolescent Therapy'),
        ('general', 'General Mental Health'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='therapist_profile')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    experience_years = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Years of professional experience"
    )
    location = models.CharField(max_length=200)
    bio = models.TextField(blank=True, help_text="Professional biography")
    qualification = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    available_days = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Comma-separated list of available days"
    )
    available_times = models.CharField(
        max_length=200,
        blank=True,
        help_text="Available time slots (e.g., 9:00-17:00)"
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    @property
    def rating(self):
        # This can be implemented later with a Rating model
        return 4.5  # Placeholder
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Therapist Profile"
        verbose_name_plural = "Therapist Profiles"

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('appointment_request', 'New Appointment Request'),
        ('appointment_confirmed', 'Appointment Confirmed'),
        ('appointment_completed', 'Session Completed'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('message_received', 'New Message Received'),
        ('profile_updated', 'Profile Updated'),
        ('availability_updated', 'Availability Updated'),
        ('client_registered', 'New Client Registered'),
    ]
    
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    related_client = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    related_appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']