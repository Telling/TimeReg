from django import forms
from TimeRegistration.models import TimeRegistration, Project, Profile


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


class OverviewPDFForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(),
        label='Project'
    )


class QuicklookForm(forms.Form):
    quick_start_date = forms.DateField()
    quick_end_date = forms.DateField()
    quick_project = forms.ModelChoiceField(
        queryset=Project.objects.filter(),
        label='Project'
    )


class ProfileForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = Profile
        fields = ('employee_id', 'department', 'employment_date')
