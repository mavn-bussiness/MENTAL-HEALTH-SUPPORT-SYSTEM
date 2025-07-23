from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('therapist', 'Therapist'),
        ('client', 'Client')
    ], default='client')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class ReadingMaterial(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='reading_materials/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_materials')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title