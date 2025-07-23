from django.db import models
from django.contrib.auth.models import User

class Therapist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)

class Appointment(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='scheduled')

class Resource(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

class SiteContent(models.Model):
    section = models.CharField(max_length=100)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

#class Profile(models.Model):
  #  user = models.OneToOneField(User, on_delete=models.CASCADE)
   # role = models.CharField(max_length=20, choices=[
      #  ('admin', 'Admin'),
       # ('therapist', 'Therapist'),
        #('client', 'Client')
    #], default='client')