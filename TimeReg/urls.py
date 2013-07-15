from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'TimeRegistration.views.home_statistics'),
    url(r'^timereg/$', 'TimeRegistration.views.time_registration'),
    url(r'^projects/$', 'TimeRegistration.views.projects'),
    url(r'^account/$', 'TimeRegistration.views.account'),
    url(r'^login/$', 'TimeRegistration.views.login_user'),
    url(r'^tools/users/$', 'TimeRegistration.views.tools_users'),
    url(r'^tools/projects/$', 'TimeRegistration.views.tools_projects'),
    url(r'^logout/$', 'TimeRegistration.views.logout_user'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
