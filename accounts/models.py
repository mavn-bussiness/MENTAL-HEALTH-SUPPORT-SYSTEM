from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from PIL import Image
import os

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('therapist', 'Therapist'),
        ('client', 'Client'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    AGE_CATEGORY_CHOICES = [
        ('13-19', '13 to 19 years'),
        ('20-35', '20 to 35 years'),
        ('35+', 'Above 35 years'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\d{10}$',
        message="Phone number must be exactly 10 digits."
    )
    
    user_id = models.CharField(max_length=10, unique=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(validators=[phone_regex], max_length=10, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    location = models.CharField(max_length=100)
    age_category = models.CharField(max_length=10, choices=AGE_CATEGORY_CHOICES, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            last_user = User.objects.filter(role='client').order_by('-id').first()
            if last_user and last_user.user_id:
                last_number = int(last_user.user_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.user_id = f"CLT{new_number:04d}"
        
        super().save(*args, **kwargs)
        
        # Resize profile image
        if self.profile_image:
            img = Image.open(self.profile_image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_image.path)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
