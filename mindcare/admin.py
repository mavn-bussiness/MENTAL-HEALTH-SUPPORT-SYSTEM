from django.contrib import admin
from .models import Therapist, Appointment, Resource, SiteContent

admin.site.register(Therapist)
admin.site.register(Appointment)
admin.site.register(Resource)
admin.site.register(SiteContent)
admin.site.register(Profile)

@admin.action(description='Generate Activity Report')
def generate_report(modeladmin, request, queryset):
    # Custom logic to generate report (e.g., count appointments)
    report = f"Total appointments: {Appointment.objects.count()}"
    modeladmin.message_user(request, report)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    actions = [generate_report]