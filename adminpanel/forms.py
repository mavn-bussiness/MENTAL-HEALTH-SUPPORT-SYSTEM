# forms.py
from django import forms
from content.models import EducationalContent
from crisis.models import CrisisResource

class EducationalContentForm(forms.ModelForm):
    class Meta:
        model = EducationalContent
        fields = [
            'title',
            'description',
            'content_type',
            'file',
            'url',
            'is_published'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

        # forms.py


class CrisisResourceForm(forms.ModelForm):
    class Meta:
        model = CrisisResource
        fields = ['title', 'description', 'phone_number', 'website', 'order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# forms.py
from notifications.models import NotificationSettings

class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = [
            'email_enabled',
            'sms_enabled',
            'push_enabled',
            'appointment_reminder_hours',
            'assessment_alert_threshold',
            'crisis_notification_recipients',
        ]
        widgets = {
            'crisis_notification_recipients': forms.SelectMultiple(attrs={'class': 'select2'}),
        }