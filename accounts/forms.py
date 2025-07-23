from django import forms
from django.contrib.auth.models import User

class TherapistRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()  # Set unusable password initially
        if commit:
            user.save()
        return user