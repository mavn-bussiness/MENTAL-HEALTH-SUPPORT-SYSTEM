from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Profile, ReadingMaterial
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from .forms import TherapistRegistrationForm
import random
import string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail

@never_cache
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'client'})
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@never_cache
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'client'})
            login(request, user)
            return redirect('dashboard' if profile.role != 'therapist' else 'therapist_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@never_cache
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    try:
        profile = request.user.profile
        if profile.role == 'admin':
            return render(request, 'dashboard/admin_dashboard.html', {'is_admin': True})
        elif profile.role == 'therapist':
            return render(request, 'dashboard/therapist_dashboard.html', {'materials': ReadingMaterial.objects.filter(uploaded_by=request.user, is_active=True)})
        else:  # client
            reading_materials = ReadingMaterial.objects.filter(is_active=True)
            return render(request, 'dashboard/client_dashboard.html', {'reading_materials': reading_materials})
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='client')
        return render(request, 'dashboard/client_dashboard.html')

@login_required
def profile_update(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='client')
    if request.method == 'POST':
        profile.role = request.POST.get('role', profile.role)
        profile.save()
        return redirect('dashboard')
    return render(request, 'registration/profile_update.html', {'profile': profile})

@login_required
def reports_analytics(request):
    try:
        profile = request.user.profile
        if profile.role == 'admin':
            today = timezone.now()
            # User Analytics
            total_users = Profile.objects.count()
            total_clients = Profile.objects.filter(role='client').count()
            total_staff = Profile.objects.exclude(role='client').count()
            week_ago = today - timedelta(days=7)
            users_week = Profile.objects.filter(user__date_joined__gte=week_ago).count()
            clients_week = Profile.objects.filter(role='client', user__date_joined__gte=week_ago).count()
            staff_week = Profile.objects.exclude(role='client', user__date_joined__gte=week_ago).count()
            month_ago = today - timedelta(days=30)
            users_month = Profile.objects.filter(user__date_joined__gte=month_ago).count()
            clients_month = Profile.objects.filter(role='client', user__date_joined__gte=month_ago).count()
            staff_month = Profile.objects.exclude(role='client', user__date_joined__gte=month_ago).count()
            year_ago = today - timedelta(days=365)
            users_year = Profile.objects.filter(user__date_joined__gte=year_ago).count()
            clients_year = Profile.objects.filter(role='client', user__date_joined__gte=year_ago).count()
            staff_year = Profile.objects.exclude(role='client', user__date_joined__gte=year_ago).count()
            # Case Analytics (Simulated)
            total_cases = 50  # Placeholder
            cases_week = 10  # Simulated
            cases_month = 40  # Simulated
            cases_year = 200  # Simulated
            return render(request, 'dashboard/reports_analytics.html', {
                'total_users': total_users, 'total_clients': total_clients, 'total_staff': total_staff,
                'users_week': users_week, 'clients_week': clients_week, 'staff_week': staff_week,
                'users_month': users_month, 'clients_month': clients_month, 'staff_month': staff_month,
                'users_year': users_year, 'clients_year': clients_year, 'staff_year': staff_year,
                'total_cases': total_cases, 'cases_week': cases_week, 'cases_month': cases_month, 'cases_year': cases_year
            })
        else:
            return redirect('dashboard')
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='client')
        return redirect('dashboard')

@login_required
def upload_material(request):
    try:
        profile = request.user.profile
        if profile.role in ['admin', 'therapist']:
            if request.method == 'POST':
                title = request.POST['title']
                file = request.FILES['file']
                material = ReadingMaterial(title=title, file=file, uploaded_by=request.user)
                material.save()
                messages.success(request, 'Material uploaded successfully.')
                return redirect('manage_resources')
            return render(request, 'dashboard/upload_material.html')
        else:
            return redirect('dashboard')
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='client')
        return redirect('dashboard')

@login_required
def manage_resources(request):
    try:
        profile = request.user.profile
        materials = ReadingMaterial.objects.filter(is_active=True)
        if request.method == 'POST':
            material_id = request.POST.get('material_id')
            if material_id:
                material = get_object_or_404(ReadingMaterial, id=material_id, is_active=True)
                if profile.role == 'admin' or material.uploaded_by == request.user:
                    material.is_active = False
                    material.save()
                    messages.success(request, 'Material deleted successfully.')
                else:
                    messages.error(request, 'You do not have permission to delete this material.')
        return render(request, 'dashboard/manage_resources.html', {'materials': materials, 'is_admin': profile.role == 'admin'})
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='client')
        return redirect('dashboard')
    except ReadingMaterial.DoesNotExist:
        messages.error(request, 'Material not found.')
        return redirect('manage_resources')

@login_required
def edit_material(request, material_id):
    material = get_object_or_404(ReadingMaterial, id=material_id, is_active=True)
    profile = request.user.profile
    if profile.role != 'admin' and material.uploaded_by != request.user:
        messages.error(request, 'You do not have permission to edit this material.')
        return redirect('manage_resources')
    if request.method == 'POST':
        material.title = request.POST['title']
        if 'file' in request.FILES:
            material.file = request.FILES['file']
        material.save()
        messages.success(request, 'Material updated successfully.')
        return redirect('manage_resources')
    return render(request, 'dashboard/edit_material.html', {'material': material})

@login_required
def delete_material(request, material_id):
    material = get_object_or_404(ReadingMaterial, id=material_id, is_active=True)
    profile = request.user.profile
    if profile.role != 'admin' and material.uploaded_by != request.user:
        messages.error(request, 'You do not have permission to delete this material.')
        return redirect('manage_resources')
    if request.method == 'POST':
        material.is_active = False
        material.save()
        messages.success(request, 'Material deleted successfully.')
        return redirect('manage_resources')
    return render(request, 'dashboard/delete_material.html', {'material': material})

@login_required
def therapist_dashboard(request):
    try:
        profile = request.user.profile
        if profile.role != 'therapist':
            return redirect('dashboard')
        materials = ReadingMaterial.objects.filter(uploaded_by=request.user, is_active=True)
        return render(request, 'dashboard/therapist_dashboard.html', {'materials': materials})
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='client')
        return redirect('dashboard')

@login_required
def register_therapist(request):
    try:
        profile = request.user.profile
        if profile.role != 'admin':
            return redirect('dashboard')
        if request.method == 'POST':
            form = TherapistRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                profile, created = Profile.objects.get_or_create(user=user)
                if not created:
                    profile.role = 'therapist'
                    profile.save()
                else:
                    profile.role = 'therapist'
                    profile.save()
                # Generate password reset token and email
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
                email_subject = 'Set Your MindCare Therapist Password'
                email_body = render_to_string('registration/password_reset_email.html', {
                    'user': user,
                    'reset_url': reset_url,
                    'site_name': 'MindCare',
                })
                send_mail(
                    email_subject,
                    email_body,
                    'kiri24121@gmail.com',  # Replace with your email
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, f'Therapist {user.username} registered successfully. A password reset link has been sent to {user.email}.')
                return redirect('dashboard')
        else:
            form = TherapistRegistrationForm()
        return render(request, 'dashboard/register_therapist.html', {'form': form})
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='client')
        return redirect('dashboard')

@login_required
def change_password(request):
    try:
        profile = request.user.profile
        if profile.role != 'therapist' or request.user.has_usable_password():
            return redirect('dashboard')
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.success(request, 'Your password has been changed successfully.')
                return redirect('therapist_dashboard')
        else:
            form = PasswordChangeForm(request.user)
        return render(request, 'dashboard/change_password.html', {'form': form})
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='client')
        return redirect('dashboard')