import random
from django.core.management.base import BaseCommand
from therapists.models import TherapistProfile
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates dummy therapist data in the database'

    def handle(self, *args, **options):
        specializations = [
            'anxiety', 'depression', 'trauma', 'relationships', 'addiction',
            'grief', 'eating_disorders', 'bipolar', 'ocd', 'adhd',
            'family_therapy', 'child_therapy', 'general'
        ]
        locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
        first_names = ['John', 'Emma', 'Michael', 'Sarah', 'David']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']

        for _ in range(10):  # Create 10 dummy therapists
            username = f"therapist_{random.randint(100, 999)}"
            email = f"{username}@mindcare.com"
            password = "testpass123"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='therapist',
                phone=f"{random.randint(1000000000, 9999999999):10d}",
                gender=random.choice(['male', 'female']),
                location=random.choice(locations)
            )

            # Extract day names from AVAILABILITY_CHOICES
            available_day_names = [day[0] for day in TherapistProfile.AVAILABILITY_CHOICES]
            selected_days = random.sample(available_day_names, k=random.randint(3, 7))

            therapist = TherapistProfile.objects.create(
                user=user,
                specialization=random.choice(specializations),
                experience_years=random.randint(1, 25),
                location=user.location,
                bio=f"Experienced therapist specializing in {random.choice(specializations)}. Dedicated to helping clients improve their mental health.",
                qualification=f"PhD in Psychology from {random.choice(locations)} University",
                license_number=f"LIC-{random.randint(1000, 9999)}",
                hourly_rate=round(random.uniform(50.0, 200.0), 2),
                available_days=','.join(selected_days),
                available_times=f"{random.randint(9, 12)}:00-{random.randint(13, 17)}:00",
                is_available=random.choice([True, False])
            )
            self.stdout.write(self.style.SUCCESS(f"Created therapist: {therapist.full_name}"))