from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip middleware for certain paths
        skip_paths = [
            '/admin/',
            '/accounts/login/',
            '/accounts/register/',
            '/accounts/logout/',
            '/crisis/',
            '/statics/',
            '/media/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Check if user is authenticated for protected views
        if not request.user.is_authenticated:
            if request.path.startswith('/assessments/') or request.path.startswith('/appointments/'):
                messages.error(request, 'Please login to access this page.')
                return redirect('accounts:login')
        
        return None 