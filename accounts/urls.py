from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),  # This defines /accounts/login/
    path('logout/', views.user_logout, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/update/', views.profile_update, name='profile_update'),  # Ensure this line is present
    path('reports-analytics/', views.reports_analytics, name='reports_analytics'),
    path('upload-material/', views.upload_material, name='upload_material'),
    path('manage-resources/', views.manage_resources, name='manage_resources'),
    path('register-therapist/', views.register_therapist, name='register_therapist'),
    path('therapist-dashboard/', views.therapist_dashboard, name='therapist_dashboard'),
    path('change-password/', views.change_password, name='change_password'),
    path('delete-material/<int:material_id>/', views.delete_material, name='delete_material'),
    path('edit-material/<int:material_id>/', views.edit_material, name='edit_material'),
]