from django import forms
from TimeRegistration.models import TimeRegistration, Project


class TimeRegForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(is_active=True),
        label='Project'
    )

    class Meta:
        model = TimeRegistration
        fields = ('date', 'start_time', 'end_time', 'hours')


class ProjectRegForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name', 'manager', 'description', 'users')
