from django import forms
from .models import EducationalContent

class ResourceForm(forms.ModelForm):
    class Meta:
        model = EducationalContent
        fields = ['title', 'description', 'content_type', 'file', 'url', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')
        if not file and not url:
            raise forms.ValidationError("Either a file or a URL must be provided.")
        return cleaned_data