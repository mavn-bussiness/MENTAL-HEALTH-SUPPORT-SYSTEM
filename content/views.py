from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EducationalContent

@login_required
def content_list(request):
    contents = EducationalContent.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'content/content_list.html', {'contents': contents}) 