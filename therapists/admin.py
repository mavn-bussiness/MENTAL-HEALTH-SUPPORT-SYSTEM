from django.contrib import admin
from .models import TherapistProfile

@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'location', 'is_available', 'created_at')
    list_filter = ('specialization', 'is_available', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'specialization', 'location')
    date_hierarchy = 'created_at'
    list_editable = ('is_available',)