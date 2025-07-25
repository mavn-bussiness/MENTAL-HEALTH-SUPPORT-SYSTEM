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
    
    # Fix for reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
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
            if self.role == 'client':
                last_user = User.objects.filter(role='client').order_by('-id').first()
                if last_user and last_user.user_id:
                    last_number = int(last_user.user_id[3:])
                    new_number = last_number + 1
                else:
                    new_number = 1
                self.user_id = f"CLT{new_number:04d}"
            elif self.role == 'therapist':
                last_user = User.objects.filter(role='therapist').order_by('-id').first()
                if last_user and last_user.user_id:
                    last_number = int(last_user.user_id[3:])
                    new_number = last_number + 1
                else:
                    new_number = 1
                self.user_id = f"THR{new_number:04d}"
            elif self.role == 'admin':
                last_user = User.objects.filter(role='admin').order_by('-id').first()
                if last_user and last_user.user_id:
                    last_number = int(last_user.user_id[3:])
                    new_number = last_number + 1
                else:
                    new_number = 1
                self.user_id = f"ADM{new_number:04d}"
        
        super().save(*args, **kwargs)
        
        # Resize profile image
        if self.profile_image:
            try:
                img = Image.open(self.profile_image.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.profile_image.path)
            except Exception as e:
                pass  # Handle image processing errors gracefully
    
    def __str__(self):
        return f"{self.username} ({self.role})"