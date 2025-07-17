from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AssessmentForm(models.Model):
    FORM_TYPE_CHOICES = [
        ('depression', 'Depression'),
        ('anxiety', 'Anxiety'),
        ('stress', 'Stress'),
        # Add more as needed
    ]
    name = models.CharField(max_length=100)
    form_type = models.CharField(max_length=20, choices=FORM_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class AssessmentResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form = models.ForeignKey(AssessmentForm, on_delete=models.CASCADE)
    responses = models.JSONField()
    total_score = models.IntegerField()
    risk_level = models.CharField(max_length=20)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.form.name} - {self.created_at.strftime('%Y-%m-%d')}"
