from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import AssessmentResponse

@receiver(post_save, sender=AssessmentResponse)
def notify_admins_on_flagged_response(sender, instance, created, **kwargs):
    if created and instance.is_flagged:
        subject = f"High-Risk Assessment Response: {instance.assessment.title}"
        message = f"""
        A high-risk assessment response was submitted.
        User: {instance.user.username}
        Assessment: {instance.assessment.title}
        Score: {instance.score}
        Risk Level: {instance.get_risk_level_display()}
        Completed: {instance.completed_at}

        Please review in the admin dashboard.
        """
        admin_emails = [user.email for user in settings.MANAGERS]
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=True,
        )