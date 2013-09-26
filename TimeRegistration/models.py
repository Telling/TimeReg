from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User)
    employee_id = models.IntegerField()
    department = models.CharField(max_length=100)
    employment_date = models.DateField()

    def __unicode__(self):
        return self.user.username


class TimeRegistration(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    week = models.IntegerField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    hours = models.FloatField()
    project = models.ForeignKey('Project')

    def __unicode__(self):
        return '{} ({})'.format(unicode(self.hours), self.project)


class Project(models.Model):
    name = models.CharField(max_length=100)
    project_id = models.IntegerField()
    manager = models.ForeignKey(
        User, null=True, blank=True, related_name='manager_of_project')
    description = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name='projects')

    def __unicode__(self):
        return '{}: {}'.format(unicode(self.project_id), self.name)
