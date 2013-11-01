from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'TimeRegistration.views.time_registration'),
    url(r'^remove_registration/(?P<timereg_id>\d+)',
        'TimeRegistration.views.remove_registration'),
    url(r'^(?P<year>\d{4})/(?P<weeknumber>\d{2})',
        'TimeRegistration.views.time_registration'),
    url(r'^(?P<year>\d{4})', 'TimeRegistration.views.time_registration'),
    url(r'^overview/$', 'TimeRegistration.views.overview'),
    url(r'^projects/$', 'TimeRegistration.views.projects'),
    url(r'^login/$', 'TimeRegistration.views.login_user'),
    url(r'^tools/users/$', 'TimeRegistration.views.tools_users'),
    url(r'^tools/projects/$', 'TimeRegistration.views.tools_projects'),
    url(r'^tools/projects/close_project/(?P<project_id>\d+)',
        'TimeRegistration.views.close_project'),
    url(r'^tools/projects/open_project/$',
        'TimeRegistration.views.open_project', name='project'),
    url(r'^tools/users/disable/$', 'TimeRegistration.views.disable_user',
        name='user'),
    url(r'^tools/users/reenable/$', 'TimeRegistration.views.reenable_user',
        name='user'),
    url(r'^tools/users/make_admin/$', 'TimeRegistration.views.do_undo_admin',
        name='user'),
    url(r'profile/', 'TimeRegistration.views.show_profile'),
    url(r'^logout/$', 'TimeRegistration.views.logout_user'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
