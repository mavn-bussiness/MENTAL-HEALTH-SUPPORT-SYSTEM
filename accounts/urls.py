from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register_client, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.client_dashboard, name='client_dashboard'),
    path('profile/', views.profile_update, name='profile_update'),
    # Add password reset and other client-related URLs as needed
]
