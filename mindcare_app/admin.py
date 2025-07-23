from django.contrib import admin
from .models import Therapist, Appointment, Resource, SiteContent

admin.site.register(Therapist)
admin.site.register(Appointment)
admin.site.register(Resource)
admin.site.register(SiteContent)