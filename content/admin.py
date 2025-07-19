from django.contrib import admin
from .models import EducationalContent

@admin.register(EducationalContent)
class EducationalContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'uploaded_by', 'is_published', 'created_at')
    list_filter = ('content_type', 'is_published', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    list_editable = ('is_published',)