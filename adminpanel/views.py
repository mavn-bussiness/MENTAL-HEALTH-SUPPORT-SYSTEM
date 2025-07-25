from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from accounts.models import User
from appointments.models import Appointment, TherapistAvailability
from assessments.models import Assessment, AssessmentResponse
from therapists.models import TherapistProfile, ActivityLog
from content.models import EducationalContent
from messaging.models import Message
from notifications.models import Notification
import json
from django.db import transaction
from content.forms import EducationalContent
from crisis.models import CrisisResource
from .forms import CrisisResourceForm
from .forms import NotificationSettingsForm
from notifications.models import NotificationSettings

@login_required
@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with key metrics and recent activities"""
    
    # Date ranges for filtering
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # User Statistics
    total_users = User.objects.count()
    new_users_week = User.objects.filter(date_joined__gte=last_7_days).count()
    clients_count = User.objects.filter(role='client').count()
    therapists_count = User.objects.filter(role='therapist').count()
    admins_count = User.objects.filter(role='admin').count()
    
    # Appointment Statistics
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
    
    # Assessment Statistics
    total_assessments = Assessment.objects.count()
    total_responses = AssessmentResponse.objects.count()
    flagged_responses = AssessmentResponse.objects.filter(is_flagged=True).count()
    responses_week = AssessmentResponse.objects.filter(completed_at__gte=last_7_days).count()
    
    # Content Statistics
    total_resources = EducationalContent.objects.count() if hasattr(EducationalContent, 'objects') else 0
    
    # Recent Activities
    recent_appointments = Appointment.objects.select_related('client', 'therapist__user').order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_responses = AssessmentResponse.objects.select_related('user', 'assessment').order_by('-completed_at')[:5]
    
    # Chart data for appointments over time
    appointment_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = Appointment.objects.filter(created_at__date=date).count()
        appointment_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    appointment_data.reverse()
    
    # Assessment completion rates by type
    assessment_types = Assessment.objects.values('assessment_type').annotate(
        total_responses=Count('assessmentresponse')
    ).order_by('-total_responses')
    
    # Therapist workload
    therapist_workload = TherapistProfile.objects.annotate(
        appointment_count=Count('therapist_appointments', filter=Q(therapist_appointments__status='confirmed'))
    ).order_by('-appointment_count')[:5]
    
    context = {
        # User stats
        'total_users': total_users,
        'new_users_week': new_users_week,
        'clients_count': clients_count,
        'therapists_count': therapists_count,
        'admins_count': admins_count,
        
        # Appointment stats
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        
        # Assessment stats
        'total_assessments': total_assessments,
        'total_responses': total_responses,
        'flagged_responses': flagged_responses,
        'responses_week': responses_week,
        
        # Content stats
        'total_resources': total_resources,
        
        # Recent data
        'recent_appointments': recent_appointments,
        'recent_users': recent_users,
        'recent_responses': recent_responses,
        
        # Chart data
        'appointment_chart_data': json.dumps(appointment_data),
        'assessment_types': assessment_types,
        'therapist_workload': therapist_workload,
    }
    
    return render(request, 'adminpanel/dashboard.html', context)


@login_required
@staff_member_required
def user_management(request):
    """User management interface"""
    
    # Get filter parameters
    role_filter = request.GET.get('role', '')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    users = User.objects.all()
    
    # Apply filters
    if role_filter:
        users = users.filter(role=role_filter)
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users.order_by('-date_joined'), 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    context = {
        'users': users_page,
        'role_filter': role_filter,
        'search_query': search_query,
        'status_filter': status_filter,
        'user_roles': User.ROLE_CHOICES,
    }
    
    return render(request, 'adminpanel/user_management.html', context)


@login_required
@staff_member_required
def user_detail(request, user_id):
    """Detailed view of a specific user"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's appointments
    if user.role == 'client':
        appointments = user.client_appointments.all()[:10]
        therapist_profile = None
    else:
        appointments = []
        try:
            therapist_profile = user.therapist_profile
        except:
            therapist_profile = None
    
    # Get user's assessment responses
    responses = user.responses.select_related('assessment').order_by('-completed_at')[:5]
    
    # Get user's messages (recent)
    sent_messages = Message.objects.filter(sender=user).count()
    received_messages = Message.objects.filter(
    room__participants=user
).exclude(sender=user).count()
    
    context = {
        'user_obj': user,  # Using user_obj to avoid conflict with request.user
        'appointments': appointments,
        'therapist_profile': therapist_profile,
        'responses': responses,
        'sent_messages': sent_messages,
        'received_messages': received_messages,
    }
    
    return render(request, 'adminpanel/user_detail.html', context)


@login_required
@staff_member_required
def therapist_management(request):
    """Therapist management interface"""
    
    # Get filter parameters
    specialization_filter = request.GET.get('specialization', '')
    availability_filter = request.GET.get('availability', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    therapists = TherapistProfile.objects.select_related('user')
    
    # Apply filters
    if specialization_filter:
        therapists = therapists.filter(specialization=specialization_filter)
    
    if availability_filter == 'available':
        therapists = therapists.filter(is_available=True)
    elif availability_filter == 'unavailable':
        therapists = therapists.filter(is_available=False)
    
    if search_query:
        therapists = therapists.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Annotate with appointment counts
    therapists = therapists.annotate(
        total_appointments=Count('therapist_appointments'),
        pending_appointments=Count('therapist_appointments', filter=Q(therapist_appointments__status='pending')),
        completed_appointments=Count('therapist_appointments', filter=Q(therapist_appointments__status='completed'))
    )
    
    # Pagination
    paginator = Paginator(therapists.order_by('-created_at'), 15)
    page_number = request.GET.get('page')
    therapists_page = paginator.get_page(page_number)
    
    context = {
        'therapists': therapists_page,
        'specialization_filter': specialization_filter,
        'availability_filter': availability_filter,
        'search_query': search_query,
        'specializations': TherapistProfile.SPECIALIZATION_CHOICES,
    }
    
    return render(request, 'adminpanel/therapist_management.html', context)


@login_required
@staff_member_required
def appointment_management(request):
    """Appointment management interface"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    therapist_filter = request.GET.get('therapist', '')
    
    # Base queryset
    appointments = Appointment.objects.select_related('client', 'therapist__user')
    
    # Apply filters
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(appointment_date__date=filter_date)
        except ValueError:
            pass
    
    if therapist_filter:
        appointments = appointments.filter(therapist_id=therapist_filter)
    
    # Pagination
    paginator = Paginator(appointments.order_by('-appointment_date'), 20)
    page_number = request.GET.get('page')
    appointments_page = paginator.get_page(page_number)
    
    # Get therapists for filter dropdown
    therapists = TherapistProfile.objects.select_related('user').all()
    
    context = {
        'appointments': appointments_page,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'therapist_filter': therapist_filter,
        'therapists': therapists,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    
    return render(request, 'adminpanel/appointment_management.html', context)


@login_required
@staff_member_required
def assessment_management(request):
    """Assessment management interface"""
    
    # Get all assessments with response counts
    assessments = Assessment.objects.annotate(
        response_count=Count('assessmentresponse'),
        flagged_count=Count('assessmentresponse', filter=Q(assessmentresponse__is_flagged=True))
    ).order_by('-created_at')
    
    # Recent responses that are flagged
    flagged_responses = AssessmentResponse.objects.filter(
        is_flagged=True
    ).select_related('user', 'assessment').order_by('-completed_at')[:10]
    
    # Assessment completion trends
    assessment_trends = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        count = AssessmentResponse.objects.filter(completed_at__date=date).count()
        assessment_trends.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    assessment_trends.reverse()
    
    context = {
        'assessments': assessments,
        'flagged_responses': flagged_responses,
        'assessment_trends': json.dumps(assessment_trends),
    }
    
    return render(request, 'adminpanel/assessment_management.html', context)


@login_required
@staff_member_required
def system_reports(request):
    """Generate various system reports"""
    
    # Date range for reports
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # User registration trends
    user_registrations = []
    for i in range(30):
        date = end_date - timedelta(days=i)
        count = User.objects.filter(date_joined__date=date).count()
        user_registrations.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    user_registrations.reverse()
    
    # Appointment status distribution
    appointment_stats = Appointment.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Assessment completion by type
    assessment_stats = AssessmentResponse.objects.values(
        'assessment__title', 'assessment__assessment_type'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Therapist performance metrics
    therapist_performance = TherapistProfile.objects.annotate(
        total_appointments=Count('therapist_appointments'),
        completed_sessions=Count(
            'therapist_appointments', 
            filter=Q(therapist_appointments__status='completed')
        ),
        avg_rating=Avg('therapist_appointments__feedback__rating')
    ).order_by('-completed_sessions')[:10]
    
    context = {
        'user_registrations': json.dumps(user_registrations),
        'appointment_stats': appointment_stats,
        'assessment_stats': assessment_stats,
        'therapist_performance': therapist_performance,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'adminpanel/system_reports.html', context)


@login_required
@staff_member_required
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {status}.")
        
        return JsonResponse({'success': True, 'status': user.is_active})
    
    return JsonResponse({'success': False})


@login_required
@staff_member_required
def update_appointment_status(request, appointment_id):
    """Update appointment status"""
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()
            
            messages.success(request, f"Appointment status updated to {new_status}.")
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
@staff_member_required
def flag_assessment_response(request, response_id):
    """Flag/unflag assessment response for review"""
    if request.method == 'POST':
        response = get_object_or_404(AssessmentResponse, id=response_id)
        response.is_flagged = not response.is_flagged
        response.save()
        
        status = "flagged" if response.is_flagged else "unflagged"
        messages.success(request, f"Assessment response has been {status}.")
        
        return JsonResponse({'success': True, 'flagged': response.is_flagged})
    
    return JsonResponse({'success': False})


@login_required
@staff_member_required
def export_data(request):
    """Export system data in various formats"""
    export_type = request.GET.get('type', 'users')
    format_type = request.GET.get('format', 'csv')
    
    # This is a placeholder for data export functionality
    # You would implement actual CSV/Excel export here
    
    if export_type == 'users':
        # Export user data
        pass
    elif export_type == 'appointments':
        # Export appointment data
        pass
    elif export_type == 'assessments':
        # Export assessment data
        pass
    
    messages.info(request, f"Export functionality for {export_type} will be implemented.")
    return redirect('adminpanel:dashboard')


@login_required
@staff_member_required
def system_settings(request):
    """System settings and configuration"""
    if request.method == 'POST':
        # Handle system settings updates
        # This would typically involve a SystemSettings model
        messages.success(request, "System settings updated successfully.")
        return redirect('adminpanel:system_settings')
    
    context = {
        'settings': {
            'maintenance_mode': False,
            'registration_enabled': True,
            'email_notifications': True,
            'max_appointments_per_day': 8,
        }
    }
    
    return render(request, 'adminpanel/system_settings.html', context)

# views.py - Add these new views

@login_required
@staff_member_required
def content_management(request):
    """Manage educational content"""
    content_type_filter = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    contents = EducationalContent.objects.all()
    
    if content_type_filter:
        contents = contents.filter(content_type=content_type_filter)
    
    if search_query:
        contents = contents.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(contents.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    contents_page = paginator.get_page(page_number)
    
    context = {
        'contents': contents_page,
        'content_type_filter': content_type_filter,
        'search_query': search_query,
        'content_types': EducationalContent.CONTENT_TYPE_CHOICES,
    }
    
    return render(request, 'adminpanel/content_management.html', context)

@login_required
@staff_member_required
def add_content(request):
    """Add new educational content"""
    if request.method == 'POST':
        form = EducationalContent(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.uploaded_by = request.user
            content.save()
            messages.success(request, "Content added successfully!")
            return redirect('adminpanel:content_management')
    else:
        form = EducationalContent()
    
    context = {'form': form}
    return render(request, 'adminpanel/add_content.html', context)

@login_required
@staff_member_required
def edit_content(request, content_id):
    """Edit existing content"""
    content = get_object_or_404(EducationalContent, id=content_id)
    
    if request.method == 'POST':
        form = EducationalContent(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, "Content updated successfully!")
            return redirect('adminpanel:content_management')
    else:
        form = EducationalContent(instance=content)
    
    context = {'form': form, 'content': content}
    return render(request, 'adminpanel/edit_content.html', context)

@login_required
@staff_member_required
def toggle_content_status(request, content_id):
    """Toggle content published status"""
    if request.method == 'POST':
        content = get_object_or_404(EducationalContent, id=content_id)
        content.is_published = not content.is_published
        content.save()
        
        status = "published" if content.is_published else "unpublished"
        messages.success(request, f"Content has been {status}.")
        
        return JsonResponse({'success': True, 'status': content.is_published})
    
    return JsonResponse({'success': False})

# views.py

@login_required
@staff_member_required
def crisis_resources(request):
    """Manage crisis support resources"""
    resources = CrisisResource.objects.all().order_by('order')
    
    if request.method == 'POST':
        form = CrisisResourceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Crisis resource added successfully!")
            return redirect('adminpanel:crisis_resources')
    else:
        form = CrisisResourceForm()
    
    context = {
        'resources': resources,
        'form': form,
    }
    return render(request, 'adminpanel/crisis_resources.html', context)

@login_required
@staff_member_required
def edit_crisis_resource(request, resource_id):
    """Edit crisis resource"""
    resource = get_object_or_404(CrisisResource, id=resource_id)
    
    if request.method == 'POST':
        form = CrisisResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, "Resource updated successfully!")
            return redirect('adminpanel:crisis_resources')
    else:
        form = CrisisResourceForm(instance=resource)
    
    context = {
        'form': form,
        'resource': resource,
    }
    return render(request, 'adminpanel/edit_crisis_resource.html', context)

@login_required
@staff_member_required
def delete_crisis_resource(request, resource_id):
    """Delete crisis resource"""
    if request.method == 'POST':
        resource = get_object_or_404(CrisisResource, id=resource_id)
        resource.delete()
        messages.success(request, "Resource deleted successfully!")
        return redirect('adminpanel:crisis_resources')
    
    return redirect('adminpanel:crisis_resources')

# views.py

@login_required
@staff_member_required
def notification_settings(request):
    """Manage notification settings"""
    settings = NotificationSettings.objects.first()
    
    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification settings updated successfully!")
            return redirect('adminpanel:notification_settings')
    else:
        form = NotificationSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'adminpanel/notification_settings.html', context)

@login_required
@staff_member_required
def notification_history(request):
    """View notification history"""
    notification_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    notifications = Notification.objects.all().order_by('-created_at')
    
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    if search_query:
        notifications = notifications.filter(
            Q(recipient__username__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    context = {
        'notifications': notifications_page,
        'notification_type': notification_type,
        'search_query': search_query,
        'notification_types': Notification.NOTIFICATION_TYPES,
    }
    
    return render(request, 'adminpanel/notification_history.html', context)