from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatbotMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_messages')
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'Bot' if self.is_bot else self.user.username}: {self.message[:30]}"
