from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('', views.assessment_list, name='assessment_list'),
    path('take/<int:assessment_id>/', views.take_assessment, name='take_assessment'),
    path('results/<int:response_id>/', views.assessment_results, name='assessment_results'),
    path('my-results/', views.user_results, name='user_results'),
]