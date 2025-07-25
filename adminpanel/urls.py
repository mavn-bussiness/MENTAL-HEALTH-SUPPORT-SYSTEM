from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    
    # Therapist Management
    path('therapists/', views.therapist_management, name='therapist_management'),
    
    # Appointment Management
    path('appointments/', views.appointment_management, name='appointment_management'),
    path('appointments/<int:appointment_id>/update-status/', views.update_appointment_status, name='update_appointment_status'),
    
    # Assessment Management
    path('assessments/', views.assessment_management, name='assessment_management'),
    path('assessments/responses/<int:response_id>/flag/', views.flag_assessment_response, name='flag_assessment_response'),

     # Content Management
    path('content/', views.content_management, name='content_management'),
    path('content/add/', views.add_content, name='add_content'),
    path('content/<int:content_id>/edit/', views.edit_content, name='edit_content'),
    path('content/<int:content_id>/toggle-status/', views.toggle_content_status, name='toggle_content_status'),

    # Crisis Resources
    path('crisis-resources/', views.crisis_resources, name='crisis_resources'),
    path('crisis-resources/<int:resource_id>/edit/', views.edit_crisis_resource, name='edit_crisis_resource'),
    path('crisis-resources/<int:resource_id>/delete/', views.delete_crisis_resource, name='delete_crisis_resource'),

     # Notifications
    path('notifications/settings/', views.notification_settings, name='notification_settings'),
    path('notifications/history/', views.notification_history, name='notification_history'),
    
    # Reports and Analytics
    path('reports/', views.system_reports, name='system_reports'),
    path('export/', views.export_data, name='export_data'),
    
    # System Settings
    path('settings/', views.system_settings, name='system_settings'),
]