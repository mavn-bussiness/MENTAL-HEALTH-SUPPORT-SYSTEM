from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Main appointment views
    path('', views.appointment_list, name='appointment_list'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('book/<int:therapist_id>/', views.book_appointment, name='book_appointment_with_therapist'),
    path('quick-book/', views.quick_appointment, name='quick_appointment'),
    path('book/success/<int:appointment_id>/', views.appointment_booking_success, name='appointment_booking_success'),
    
    # Appointment detail and management
    path('<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<int:appointment_id>/feedback/', views.appointment_feedback, name='appointment_feedback'),
    path('<int:appointment_id>/notes/', views.therapist_notes, name='therapist_notes'),
    path('<int:appointment_id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    
    # Appointment lists and filtering
    path('upcoming/', views.upcoming_appointments, name='upcoming_appointments'),
    path('past/', views.past_appointments, name='past_appointments'),
    
    # Therapist availability
    path('availability/', views.therapist_availability, name='therapist_availability'),
    
    # AJAX endpoints
    path('check-availability/', views.check_availability, name='check_availability'),
]