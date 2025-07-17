from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=10, required=True)
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=True)
    location = forms.CharField(max_length=100, required=True)
    age_category = forms.ChoiceField(choices=User.AGE_CATEGORY_CHOICES, required=True)
    profile_image = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone', 'gender', 'location', 'age_category', 'profile_image')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-3'),
                Column('gender', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('location', css_class='form-group col-md-6 mb-3'),
                Column('age_category', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'profile_image',
            Submit('submit', 'Register', css_class='btn btn-primary')
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.gender = self.cleaned_data['gender']
        user.location = self.cleaned_data['location']
        user.age_category = self.cleaned_data['age_category']
        user.role = 'client'
        
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username_or_email',
            'password',
            Submit('submit', 'Login', css_class='btn btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')
        
        if username_or_email and password:
            # Try to find user by username or email
            try:
                if '@' in username_or_email:
                    user = User.objects.get(email=username_or_email)
                else:
                    user = User.objects.get(username=username_or_email)
                
                user = authenticate(username=user.username, password=password)
                if not user:
                    raise forms.ValidationError("Invalid credentials")
                
                cleaned_data['user'] = user
            except User.DoesNotExist:
                raise forms.ValidationError("User not found")
        
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'gender', 'location', 'age_category', 'profile_image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-3'),
                Column('gender', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('location', css_class='form-group col-md-6 mb-3'),
                Column('age_category', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'profile_image',
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        ) 