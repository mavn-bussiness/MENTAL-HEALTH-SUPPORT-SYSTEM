# crisis/models.py
from django.db import models

class CrisisResource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.title

