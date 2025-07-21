from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.chatbot_dashboard, name='chatbot_dashboard'),
    path('get-response/', views.chatbot_response, name='chatbot_response'),
] 