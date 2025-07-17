from django import forms
from .models import Appointment
from therapists.models import TherapistProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class AppointmentRequestForm(forms.ModelForm):
    therapist = forms.ModelChoiceField(
        queryset=TherapistProfile.objects.filter(is_active=True, is_verified=True),
        empty_label="Select a therapist"
    )
    
    class Meta:
        model = Appointment
        fields = ['therapist', 'appointment_date', 'client_notes']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'client_notes': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'therapist',
            Row(
                Column('appointment_date', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'client_notes',
            Submit('submit', 'Request Appointment', css_class='btn btn-primary')
        ) 