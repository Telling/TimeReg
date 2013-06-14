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

    def __unicode__(self):
        return unicode(self.hours)
