from django import forms
from TimeRegistration.models import TimeRegistration, Project


class TimeRegForm(forms.ModelForm):
    class Meta:
        model = TimeRegistration
        fields = ('date', 'start_time', 'end_time', 'hours', 'project')


class ProjectRegForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'manager', 'description', 'users')
