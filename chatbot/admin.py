from django.contrib import admin
from .models import ChatbotMessage

@admin.register(ChatbotMessage)
class ChatbotMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_bot', 'message', 'timestamp')
    list_filter = ('is_bot', 'timestamp', 'user')
    search_fields = ('message', 'user__username')
