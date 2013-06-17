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
    date = models.DateTimeField()
    hours = models.FloatField()
    project = models.OneToOneField('Project')

    def __unicode__(self):
        return unicode(self.hours)


class Project(models.Model):
    project_name = models.CharField(max_length=100)
    project_id = models.IntegerField()
    project_manager = models.ForeignKey(User, null=True, blank=True)
    project_desc = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.project_id
