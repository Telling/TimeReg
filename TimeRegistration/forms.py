from django import forms
from django.contrib.auth.models import User
from TimeRegistration.models import TimeRegistration, Profile
from TimeRegistration.models import Project, Project_phase


class TimeRegForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(TimeRegForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(
            is_active=True, users=user
        )

    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        label="Project",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = TimeRegistration
        fields = ('date', 'start_time', 'description', 'end_time', 'hours')


class ProjectRegForm(forms.ModelForm):
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label='Manager',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        label='Users',
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Project
        fields = ('name', 'description', 'users', 'manager')


class ProjectPhaseCreateForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(is_active=True),
        label='Project',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        label='Users',
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Project_phase
        fields = ('name', 'description', 'users', 'project')


class OverviewPDFForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(),
        label='Project',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class QuicklookForm(forms.Form):
    quick_start_date = forms.DateField()
    quick_end_date = forms.DateField()
    quick_project = forms.ModelChoiceField(
        queryset=Project.objects.filter(),
        label='Project',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ProfileForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = Profile
        fields = ('employee_id', 'department', 'employment_date')


class UploadIcsForm(forms.Form):
    ics_file = forms.FileField()
    projects = forms.ModelChoiceField(
        queryset=Project.objects.filter(is_active=True),
        required=False,
        label='Projects',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
