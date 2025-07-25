from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EducationalContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('tip', 'Mental Health Tip'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='article')
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    url = models.URLField(blank=True, null=True, help_text="Optional URL for external resources")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_resources')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Educational Content"
        verbose_name_plural = "Educational Contents"