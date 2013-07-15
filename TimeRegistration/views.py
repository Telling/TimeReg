from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.contrib import messages
from TimeRegistration.models import TimeRegistration, Project
from django.db.models import Sum, Avg


def login_user(request):
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                messages.warning(request, 'Inactive account.')
        else:
            messages.warning(
                request, 'Your username and/or password were incorrect.')

    return redirect('/')


def home_statistics(request):
    context = {}
    if request.user.is_authenticated():
        timeregistrations = TimeRegistration.objects.filter(
            user=request.user)

        context['timeregistrations'] = timeregistrations.order_by('-hours')

        projects = Project.objects.filter(
            timeregistration__user=request.user).annotate(
                total_hours=Sum('timeregistration__hours')
            ).order_by('-total_hours')

        context['projects'] = projects

        # Calculate the average daily hours
        def average_daily_hours():
            average_pr_day = timeregistrations \
                .extra(select={
                    'd': 'extract(day FROM date)',
                    'm': 'extract(month FROM date)',
                    'y': 'extract(year FROM date)'
                }) \
                .values('d', 'm', 'y') \
                .annotate(avg_hours=Avg('hours'))

            total_hours_by_day = 0.0
            for i in range(len(average_pr_day)):
                total_hours_by_day += average_pr_day[i]['avg_hours']

            return total_hours_by_day / len(average_pr_day)

        context['average_daily'] = average_daily_hours()

        # Calculate the average weekly hours
        def average_weekly_hours():
            average_pr_week = timeregistrations \
                .extra(select={'y': 'extract(year FROM date)'}) \
                .values('week', 'y') \
                .annotate(avg_hours=Avg('hours'))

            total_hours_by_week = 0.0
            for i in range(len(average_pr_week)):
                total_hours_by_week += average_pr_week[i]['avg_hours']

            return total_hours_by_week / len(average_pr_week)

        context['average_weekly'] = average_weekly_hours()

        # Calculate the average monthly hours
        def average_monthly_hours():
            average_pr_month = timeregistrations \
                .extra(select={
                    'm': 'extract(month FROM date)',
                    'y': 'extract(year FROM date)'
                }) \
                .values('m', 'y') \
                .annotate(avg_hours=Avg('hours'))

            total_hours_by_month = 0.0
            for i in range(len(average_pr_month)):
                total_hours_by_month += average_pr_month[i]['avg_hours']

            return total_hours_by_month / len(average_pr_month)

        context['average_monthly'] = average_monthly_hours()

    return render_to_response('index.html', RequestContext(request, context))


def logout_user(request):
    logout(request)
    messages.success(request, 'You\'ve been logged out successfully!')
    return redirect('/')


def account(request):
    return render_to_response('account.html', RequestContext(request))


def projects(request):
    return render_to_response('projects.html', RequestContext(request))


def time_registration(request):
    return render_to_response('timeregistration.html', RequestContext(request))


def tools_users(request):
    return render_to_response('tools_users.html', RequestContext(request))


def tools_projects(request):
    return render_to_response('tools_projects.html', RequestContext(request))
