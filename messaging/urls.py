from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Main chat pages
    path('', views.chat_dashboard, name='chat_dashboard'),
    path('room/<uuid:room_id>/', views.chat_room, name='chat_room'),
    
    # Chat actions
    path('start-chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('room/<uuid:room_id>/send/', views.send_message, name='send_message'),
    path('room/<uuid:room_id>/load-messages/', views.load_messages, name='load_messages'),
    
    # User management
    path('block-user/<int:user_id>/', views.block_user, name='block_user'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
]