from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User

class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ('phq9', 'PHQ-9 (Depression)'),
        ('gad7', 'GAD-7 (Anxiety)'),
        ('pcl5', 'PCL-5 (PTSD)'),
        ('custom', 'Custom Assessment'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.CharField(max_length=10, default='1.0')
    min_score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=27)  # Default for PHQ-9
    
    def __str__(self):
        return f"{self.title} (v{self.version})"

class Question(models.Model):
    QUESTION_TYPES = [
        ('likert', 'Likert Scale'),
        ('multiple', 'Multiple Choice'),
        ('text', 'Text Response'),
    ]
    
    assessment = models.ForeignKey(Assessment, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='likert')
    order = models.PositiveIntegerField(default=0)
    weight = models.FloatField(default=1.0)  # For weighted scoring
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}..."

class LikertOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    value = models.IntegerField()
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.text} ({self.value})"

class AssessmentResponse(models.Model):
    RISK_LEVELS = [
        ('none', 'None/Minimal'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('moderately_severe', 'Moderately Severe'),
        ('severe', 'Severe'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.IntegerField()
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    completed_at = models.DateTimeField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)  # For clinical review
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username}'s {self.assessment.title} response"

class ResponseAnswer(models.Model):
    response = models.ForeignKey(AssessmentResponse, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_value = models.IntegerField(null=True, blank=True)
    answer_text = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Answer to Q{self.question.order}"

class Recommendation(models.Model):
    assessment = models.ForeignKey(Assessment, related_name='recommendations', on_delete=models.CASCADE)
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    risk_level = models.CharField(max_length=20, choices=AssessmentResponse.RISK_LEVELS)
    title = models.CharField(max_length=200)
    description = models.TextField()
    action_items = models.TextField(help_text="Bullet-point list of actions")
    # Fixed: Changed from 'resources.EducationalContent' to 'content.EducationalContent'
    resources = models.ManyToManyField('content.EducationalContent', blank=True)
    
    class Meta:
        ordering = ['assessment', 'min_score']
    
    def __str__(self):
        return f"{self.title} ({self.min_score}-{self.max_score})"