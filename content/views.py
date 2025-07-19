from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EducationalContent
from .forms import ResourceForm

def resource_list(request):
    """List all published resources"""
    resources = EducationalContent.objects.filter(is_published=True).order_by('-created_at')
    context = {'resources': resources}
    return render(request, 'content/resource_list.html', context)

def resource_detail(request, pk):
    """Display details of a specific resource"""
    resource = get_object_or_404(EducationalContent, pk=pk, is_published=True)
    context = {'resource': resource}
    return render(request, 'content/resource_detail.html', context)

@login_required
def resource_upload(request):
    """Allow admins to upload new resources"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admins only.')
        return redirect('resources:resource_list')
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, 'Resource uploaded successfully!')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm()
    
    return render(request, 'content/resource_upload.html', {'form': form})

@login_required
def resource_edit(request, pk):
    """Allow admins to edit existing resources"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admins only.')
        return redirect('resources:resource_list')
    
    resource = get_object_or_404(EducationalContent, pk=pk)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully!')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm(instance=resource)
    
    return render(request, 'content/resource_upload.html', {'form': form, 'resource': resource})

@login_required
def resource_delete(request, pk):
    """Allow admins to delete resources"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admins only.')
        return redirect('resources:resource_list')
    
    resource = get_object_or_404(EducationalContent, pk=pk)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted successfully!')
        return redirect('resources:resource_list')
    
    return render(request, 'content/resource_delete.html', {'resource': resource})