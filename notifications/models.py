# notifications/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationSettings(models.Model):
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    appointment_reminder_hours = models.PositiveIntegerField(
        default=24,
        help_text="How many hours before appointment to send reminder"
    )
    assessment_alert_threshold = models.PositiveIntegerField(
        default=15,
        help_text="Assessment scores above this will trigger alerts"
    )
    crisis_notification_recipients = models.ManyToManyField(
        User,
        limit_choices_to={'role': 'admin'},
        help_text="Staff who receive crisis notifications"
    )
    
    def __str__(self):
        return "Notification Settings"
    
    class Meta:
        verbose_name_plural = "Notification Settings"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('appointment', 'Appointment'),
        ('assessment', 'Assessment'),
        ('message', 'Message'),
        ('crisis', 'Crisis Alert'),
        ('system', 'System'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.recipient.username}"