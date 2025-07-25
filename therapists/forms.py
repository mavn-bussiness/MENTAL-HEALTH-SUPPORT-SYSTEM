from django import forms
from .models import TherapistProfile

class TherapistProfileForm(forms.ModelForm):
    class Meta:
        model = TherapistProfile
        fields = ['specialization', 'experience_years', 'location', 'bio', 'qualification', 'license_number', 'hourly_rate']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class TherapistAvailabilityForm(forms.ModelForm):
    available_days = forms.MultipleChoiceField(
        choices=TherapistProfile.AVAILABILITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = TherapistProfile
        fields = ['available_days', 'available_times', 'is_available']
        widgets = {
            'available_times': forms.TextInput(attrs={'placeholder': 'e.g., 9:00-17:00'}),
        }

    def clean_available_days(self):
        days = self.cleaned_data.get('available_days')
        if days:
            return ','.join(days)
        return ''