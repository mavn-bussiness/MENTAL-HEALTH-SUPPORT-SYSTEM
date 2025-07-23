from django.contrib import admin
from .models import Profile
from .models import Profile, ReadingMaterial
#from mindcare_app.models import Therapist  # Import Therapist model

admin.site.register(Profile)
#admin.site.register(Therapist)
admin.site.register(ReadingMaterial)