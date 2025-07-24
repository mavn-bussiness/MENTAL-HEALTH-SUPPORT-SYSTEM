from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_dashboard, name='chatbot_dashboard'),  # Root path for chatbot
    path('dashboard/', views.chatbot_dashboard, name='chatbot_dashboard_alt'),  # Keep for backward compatibility
    path('get-response/', views.chatbot_response, name='chatbot_response'),
]