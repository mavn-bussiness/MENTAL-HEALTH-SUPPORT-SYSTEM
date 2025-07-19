from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User

class ClientRegistrationForm(UserCreationForm):
    username=forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=10, required=True)
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=True)
    location = forms.CharField(max_length=100, required=True)
    age_category = forms.ChoiceField(choices=User.AGE_CATEGORY_CHOICES, required=False)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'gender', 'location', 'age_category', 'profile_image', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.gender = self.cleaned_data['gender']
        user.location = self.cleaned_data['location']
        user.age_category = self.cleaned_data.get('age_category')
        if commit:
            user.save()
            if self.cleaned_data['profile_image']:
                user.profile_image = self.cleaned_data['profile_image']
                user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(label="Username or Email", max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Check if username is actually an email
            user_obj = User.objects.filter(email=username).first() or User.objects.filter(username=username).first()
            if user_obj:
                user = authenticate(username=user_obj.username, password=password)
                if user is not None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data

        raise forms.ValidationError("Invalid username/email or password.")

    username = forms.CharField(label="Username or Email", max_length=254)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = User.objects.filter(email=username).first() or User.objects.filter(username=username).first()
            if user:
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError("Invalid username/email or password.")
        return super().clean()

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'gender', 'location', 'age_category', 'profile_image']

class PasswordResetForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="New Password")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data