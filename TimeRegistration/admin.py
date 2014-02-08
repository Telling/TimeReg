from django.contrib import admin
from .models import Profile, TimeRegistration, Project, Project_phase

admin.site.register(Profile)
admin.site.register(TimeRegistration)
admin.site.register(Project)
admin.site.register(Project_phase)
