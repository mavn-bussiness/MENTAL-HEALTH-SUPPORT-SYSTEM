from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register_client, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.client_dashboard, name='client_dashboard'),
    path('profile/update/', views.profile_update, name='profile_update'),
     path('profile/update/success/', views.profile_update_success, name='profile_update_success'),
    path('password/reset/', views.password_reset_request, name='password_reset_request'),
    path('password/reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]