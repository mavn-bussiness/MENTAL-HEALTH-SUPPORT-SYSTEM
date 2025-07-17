from django.db import models
from django.contrib.auth import get_user_model
from therapists.models import TherapistProfile

User = get_user_model()

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    therapist = models.ForeignKey(TherapistProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    duration = models.IntegerField(default=60)  # in minutes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    client_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f"{self.client.username} - {self.therapist.full_name} - {self.appointment_date}"
