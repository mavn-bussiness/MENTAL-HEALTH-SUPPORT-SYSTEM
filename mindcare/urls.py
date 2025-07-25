"""
URL configuration for mindcare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path ,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('resources/', include('content.urls', namespace='resources')),
    path('therapists/', include('therapists.urls', namespace='therapists')),
    path('assessments/',include('assessments.urls', namespace='assessments')),
    path('messaging/', include('messaging.urls')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('chatbot/', include('chatbot.urls', namespace='chatbot')),
    path('adminpanel/', include('adminpanel.urls', namespace='adminpanel')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

