from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.contrib import messages
from django.utils import timezone
from django.db.models import Max, Sum
from django.http import HttpResponse
from django.contrib.auth.models import User
from TimeRegistration.models import TimeRegistration, Project, Profile
from TimeRegistration.forms import TimeRegForm, ProjectRegForm, ProfileForm
from TimeRegistration.forms import OverviewPDFForm, QuicklookForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
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


def projects(request):
    if request.user.is_authenticated():
        context = {}

        projects = request.user.projects.all().annotate(
            total_hours=Sum('timeregistration__hours')).order_by('project_id')

        open_projects = projects.filter(is_active=True)
        context['open_projects'] = open_projects

        closed_projects = projects.filter(is_active=False)
        context['closed_projects'] = closed_projects

        return render_to_response('projects.html',
                                  RequestContext(request, context))
    else:
        return render_to_response('index.html', RequestContext(request))


def create_pdf(user, project, start_date, end_date):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'
    pdf = canvas.Canvas(response, pagesize=A4)
    pdf.setFont('Helvetica', 10)

    registrations = TimeRegistration.objects.filter(
        user=user,
        project=project,
        date__range=['{}'.format(start_date), '{}'.format(end_date)]
    ).order_by('date')

    hour_sum = registrations.aggregate(Sum('hours'))

    pdf.drawString(
        70, 760, 'Time registrations for {} - {} ({})'.format(
            start_date, end_date, project.name
        ))
    pdf.setLineWidth(.3)
    pdf.line(70, 755, 525, 755)

    pdf.setDash(1, 2)

    pdf_text = 725
    pdf_line = 720
    for i in range(0, len(registrations)):
        pdf.drawString(100, pdf_text, '{}'.format(
            registrations[i].date.strftime('%d-%m-%Y')))
        pdf.drawString(500, pdf_text, '{}'.format(registrations[i].hours))
        pdf.line(100, pdf_line, 525, pdf_line)
        pdf_text -= 20
        pdf_line = pdf_text - 5
        if i != 0 and i % 31 == 0:
            pdf.showPage()
            pdf.setFont('Helvetica', 10)
            pdf.setDash(1, 2)
            pdf_text = 725
            pdf_line = 720

    pdf.setDash()
    pdf.drawString(420, 85, 'Total:')
    pdf.setLineWidth(1)
    pdf.line(420, 80, 525, 80)
    pdf.drawString(502, 85, '{}'.format(hour_sum['hours__sum']))

    pdf.setFont('Helvetica', 6)
    pdf.setLineWidth(.3)
    pdf.line(70, 60, 525, 60)
    pdf.drawString(70, 50, 'Exported from TimeReg')

    pdf.showPage()
    pdf.save()
    return response


def overview(request):
    context = {}

    # Check if the post request contains the buttons html names
    quicklook = 'quicklook' in request.POST
    export = 'export' in request.POST

    if request.method == 'POST' and quicklook is True:
        quicklook_form = QuicklookForm(request.POST)

        if quicklook_form.is_valid():
            start_date = quicklook_form.cleaned_data['quick_start_date']
            context['start_date'] = start_date
            end_date = quicklook_form.cleaned_data['quick_end_date']
            context['end_date'] = end_date
            registrations = TimeRegistration.objects.filter(
                user=request.user,
                project=quicklook_form.cleaned_data['quick_project'],
                date__range=['{}'.format(start_date), '{}'.format(end_date)]
            ).order_by('date')

            if not registrations:
                context['empty_registrations'] = True
            else:
                context['registrations'] = registrations
                hour_sum = registrations.aggregate(Sum('hours'))
                context['total_hours'] = hour_sum['hours__sum']
    else:
        quicklook_form = QuicklookForm()

    if request.method == 'POST' and export is True:
        pdf_form = OverviewPDFForm(request.POST)

        if pdf_form.is_valid():
            user = request.user
            project = pdf_form.cleaned_data['project']
            start_date = pdf_form.cleaned_data['start_date']
            end_date = pdf_form.cleaned_data['end_date']

            return create_pdf(user, project, start_date, end_date)
    else:
        pdf_form = OverviewPDFForm()

    context['pdf_form'] = pdf_form
    context['quicklook_form'] = quicklook_form
    return render_to_response('overview.html',
                              RequestContext(request, context))


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
            context['weeknumber'] = weeknumber
        elif year:
            weeknumber = date.today().isocalendar()[1]
            registrations = registrations.filter(
                user=request.user,
                date__year=year,
                week=weeknumber
            ).order_by('-date')
            context['weeknumber'] = weeknumber
        elif year and weeknumber:
            registrations = registrations.filter(
                user=request.user,
                date__year=year,
                week=weeknumber
            ).order_by('-date')
            context['weeknumber'] = weeknumber
        else:
            weeknumber = date.today().isocalendar()[1]
            registrations = registrations.filter(
                user=request.user,
                date__year='{}'.format(today.year),
                week=weeknumber
            ).order_by('-date')
            context['weeknumber'] = weeknumber

        context['registrations'] = registrations

        if request.method == "POST":
            form = TimeRegForm(request.POST)
            if form.is_valid():
                timeregistration = form.save(commit=False)
                timeregistration.user = request.user
                timeregistration.week = form.cleaned_data[
                    'date'].isocalendar()[1]
                timeregistration.project = form.cleaned_data['project']
                timeregistration.save()
                messages.success(request,
                                 'Successfully added {} hours on {}'.format(
                                     timeregistration.hours,
                                     timeregistration.date
                                 ))
                return redirect('/')
        else:
            form = TimeRegForm()

        context['form'] = form

        return render_to_response('index.html',
                                  RequestContext(request, context))
    else:
        return render_to_response('index.html', RequestContext(request))


def tools_users(request):
    context = {}

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST)
        if profile_form.is_valid():
            username = profile_form.cleaned_data['username']
            email = profile_form.cleaned_data['email']
            password = profile_form.cleaned_data['password']

            # Create user object
            user = User.objects.create_user('{}'.format(username),
                                            '{}'.format(email),
                                            '{}'.format(password)
                                            )

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.employee_id = profile_form.cleaned_data['employee_id']
            profile.department = profile_form.cleaned_data['department']
            profile.employment_date = profile_form.cleaned_data[
                'employment_date']
            profile.save()
            messages.success(
                request, 'Successfully added user {}'.format(username))
            return redirect('/tools/users/')
    else:
        profile_form = ProfileForm()

    context['profile_form'] = profile_form

    context['active_users'] = Profile.objects.filter(is_active=True)
    context['disabled_users'] = Profile.objects.filter(is_active=False)

    return render_to_response('tools_users.html',
                              RequestContext(request, context))


def disable_user(request):
    username = request.GET['user']
    Profile.objects.filter(user__username=username).update(is_active=False)
    messages.success(request, 'Successfully disabled user {}'.format(
        username))

    return redirect('/tools/users/')


def reenable_user(request):
    username = request.GET['user']
    Profile.objects.filter(user__username=username).update(is_active=True)
    messages.success(request, 'Successfully re-enabled user {}'.format(
        username))
    return redirect('/tools/users')


def tools_projects(request):
    context = {}

    projects = Project.objects.filter().order_by('project_id')

    def next_project_id():
        current_id = projects.aggregate(Max('project_id'))['project_id__max']
        if current_id is None:
            return 0
        else:
            return current_id

    if request.method == 'POST':
        form = ProjectRegForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.project_id = next_project_id() + 1
            project.is_active = True
            project.save()
            form.save_m2m()
            messages.success(request, 'Successfully added project {}'.format(
                project.name))
            return redirect('/tools/projects/')
    else:
        form = ProjectRegForm()

    context['project_form'] = form

    active_projects = projects.filter(is_active=True).order_by('project_id')
    context['active_projects'] = active_projects

    closed_projects = projects.filter(is_active=False).order_by('project_id')
    context['closed_projects'] = closed_projects

    return render_to_response('tools_projects.html',
                              RequestContext(request, context))


def close_project(request, project_id):
    Project.objects.filter(project_id=project_id).update(is_active=False)
    messages.success(request, 'Successfully closed project #{}'.format(
        project_id))

    return redirect('/tools/projects/')


def open_project(request):
    project_id = request.GET['project']
    Project.objects.filter(project_id=project_id).update(is_active=True)
    messages.success(request, 'Successfully reopened project #{}'.format(
        project_id))

    return redirect('/tools/projects/')


def remove_registration(request, timereg_id):
    TimeRegistration.objects.filter(id=timereg_id).delete()
    messages.success(request, 'Successfully removed registration')

    return redirect('/')
