from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.contrib import messages
from django.utils import timezone
from django.db.models import Max, Sum
from TimeRegistration.models import TimeRegistration
from TimeRegistration.forms import TimeRegForm, ProjectRegForm
from datetime import date


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


def logout_user(request):
    logout(request)
    messages.success(request, 'You\'ve been logged out successfully!')
    return redirect('/')


def account(request):
    return render_to_response('account.html', RequestContext(request))


def projects(request):
    context = {}

    projects = request.user.projects.all().annotate(
        total_hours=Sum('timeregistration__hours')).order_by('project_id')

    open_projects = projects.filter(is_active=True)
    context['open_projects'] = open_projects

    closed_projects = projects.filter(is_active=False)
    context['closed_projects'] = closed_projects

    return render_to_response('projects.html',
                              RequestContext(request, context))


def overview(request):
    return render_to_response('overview.html', RequestContext(request))


def time_registration(request, year=None, weeknumber=None):
    if request.user.is_authenticated():
        context = {}

        today = timezone.now()
        context['current_date'] = '{}-{:0>2}-{:0>2}'.format(
            today.year, today.month, today.day)

        if year:
            context['last_year'] = int(year) - 1
            context['current_year'] = year
            context['next_year'] = int(year) + 1
        else:
            context['last_year'] = '{}'.format(today.year - 1)
            context['current_year'] = '{}'.format(today.year)
            context['next_year'] = '{}'.format(today.year + 1)

        registrations = TimeRegistration.objects.filter(
            user=request.user).order_by('-date')

        if weeknumber:
            registrations = registrations.filter(
                user=request.user,
                date__year='{}'.format(today.year),
                week=weeknumber
            ).order_by('-date')
        elif year:
            registrations = registrations.filter(
                user=request.user,
                date__year=year,
                week=date.today().isocalendar()[1]
            ).order_by('-date')
        elif year and weeknumber:
            registrations = registrations.filter(
                user=request.user,
                date__year=year,
                week=weeknumber
            ).order_by('-date')
        else:
            registrations = registrations.filter(
                user=request.user,
                date__year='{}'.format(today.year),
                week=date.today().isocalendar()[1]
            ).order_by('-date')

        context['registrations'] = registrations

        if request.method == "POST":
            form = TimeRegForm(request.POST)
            if form.is_valid():
                timeregistration = form.save(commit=False)
                timeregistration.user = request.user
                timeregistration.week = form.cleaned_data[
                    'date'].isocalendar()[1]
                timeregistration.save()
                return redirect('/')
        else:
            form = TimeRegForm()

        context['form'] = form

        return render_to_response('index.html',
                                  RequestContext(request, context))
    else:
        return render_to_response('index.html', RequestContext(request))


def tools_users(request):
    return render_to_response('tools_users.html', RequestContext(request))


def tools_projects(request):
    context = {}

    def next_project_id():
        current_id = projects.aggregate(Max('project_id'))['project_id__max']
        if current_id is None:
            return 0
        else:
            return current_id + 1

    if request.method == "POST":
        form = ProjectRegForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.project_id = next_project_id()
            project.is_active = True
            project.save()
            form.save_m2m()
            return redirect('/tools/projects/')
    else:
        form = ProjectRegForm()

    context['project_form'] = form
    return render_to_response('tools_projects.html',
                              RequestContext(request, context))
