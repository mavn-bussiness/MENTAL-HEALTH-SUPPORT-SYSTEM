from django.urls import path
from . import views

app_name = 'therapists'

urlpatterns = [
    path('', views.therapist_directory, name='therapist_directory'),
    path('<int:pk>/', views.therapist_detail, name='therapist_detail'),
    path('dashboard/', views.therapist_dashboard, name='therapist_dashboard'),
    path('profile/edit/', views.therapist_profile_edit, name='therapist_profile_edit'),
    path('availability/', views.therapist_availability, name='therapist_availability'),
]