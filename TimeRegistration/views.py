from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils import simplejson as json
from django.db.models import Max, Sum
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core import serializers
from TimeRegistration.models import TimeRegistration, Project, Profile
from TimeRegistration.models import Project_phase
from TimeRegistration.forms import TimeRegForm, ProjectRegForm, ProfileForm
from TimeRegistration.forms import OverviewPDFForm, QuicklookForm
from TimeRegistration.forms import UploadIcsForm, ProjectPhaseCreateForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import date, datetime
from icalendar import Calendar
from calendar import HTMLCalendar


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
                messages.warning(request, 'Disabled account.')
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


class RegistrationCalendar(HTMLCalendar):

    def __init__(self, registrations):
        super(RegistrationCalendar, self).__init__()
        date_list = []
        for reg in registrations:
            date_list.append(reg.date.day)

        self.dates_of_registrations = date_list

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.dates_of_registrations:
                cssclass += ' filled'
            return self.day_cell(cssclass, day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(RegistrationCalendar, self).formatmonth(year, month)

    def formatmonthname(self, year, month, withyear=True):
        return ""

    def day_cell(self, cssclass, body):
        if body != '&nbsp;':
            body = '<a href="/{:02d}/{:02d}/{:02d}">{}<a/>'.format(
                self.year,
                self.month,
                body,
                body
            )
        return '<td class="{}">{}</td>'.format(cssclass, body)


# Adds the correct month ints and names to the month switcher in index.html
def month_switch(context_dict, month, year):
    today = timezone.now()

    # List to index into instead of calculating month name every time
    month_names = [
        '', 'January', 'February', 'March', 'April', 'May',
        'June', 'July', 'August', 'September', 'October',
        'November', 'December'
    ]

    def calc_months(context_dict, month, year):
        if int(month) is 12:
            context_dict['next_month'] = '{:02d}'.format(1)
            context_dict['month_l_year'] = int(year)
            context_dict['month_r_year'] = int(year) + 1
        elif int(month) is 1:
            context_dict['last_month'] = 12
            context_dict['month_l_year'] = int(year) - 1
            context_dict['month_r_year'] = int(year)
            context_dict['next_month'] = '{:02d}'.format(2)
        else:
            context_dict['next_month'] = '{:02d}'.format(int(month) + 1)
            context_dict['month_r_year'] = year
            context_dict['month_l_year'] = year

    if month:
        context_dict['last_month'] = '{:02d}'.format(int(month) - 1)
        context_dict['month_name'] = month_names[int(month)]

        calc_months(context_dict, month, year)
    else:
        year = today.year
        month = today.month

        context_dict['last_month'] = '{:02d}'.format(int(month) - 1)
        context_dict['month_name'] = month_names[int(month)]

        calc_months(context_dict, month, year)


# Adds the correct years to the year switcher in index.html
def year_switch(context_dict, year):
    today = timezone.now()

    if year:
        context_dict['last_year'] = int(year) - 1
        context_dict['current_year'] = year
        context_dict['next_year'] = int(year) + 1
    else:
        context_dict['last_year'] = '{}'.format(today.year - 1)
        context_dict['current_year'] = '{}'.format(today.year)
        context_dict['next_year'] = '{}'.format(today.year + 1)


def list_project_phases(request):
    project = request.GET['project']
    active = False

    if 'active' in request.GET:
        active = True

    if project:
        project_phases = Project_phase.objects.filter(
            users=request.user,
            project=project,
            is_active=active
        )
        data = serializers.serialize("json", project_phases)
        return HttpResponse(json.dumps(data), content_type="application/json")

    return HttpResponse()


def time_registration(request, year=None, month=None, day=None):
    if request.user.is_authenticated():
        context = {}

        today = timezone.now()
        context['current_date'] = '{}-{:0>2}-{:0>2}'.format(
            today.year, today.month, today.day)

        year_switch(context, year)

        month_switch(context, month, year)

        registrations = TimeRegistration.objects.filter(
            user=request.user).order_by('-date')

        if year and month and day:
            date = datetime(int(year), int(month), int(day))
            context['day'] = date.strftime("%d")
            registrations = registrations.filter(
                user=request.user,
                date__year=year,
                date__month=month,
                date__day=day
            ).order_by('-start_time')

            context['calendar'] = mark_safe(
                RegistrationCalendar(registrations).formatmonth(
                    int(year), int(month)
                )
            )
        elif year and month:
            registrations = registrations.filter(
                user=request.user,
                date__year=year,
                date__month=month
            ).order_by('-date')

            context['calendar'] = mark_safe(
                RegistrationCalendar(registrations).formatmonth(
                    int(year), int(month)
                )
            )
        elif year:
            month = today.month
            registrations = registrations.filter(
                user=request.user,
                date__year=year,
                date__month=month
            ).order_by('-date')

            context['calendar'] = mark_safe(
                RegistrationCalendar(registrations).formatmonth(
                    int(year), int(month)
                )
            )
        else:
            month = today.month
            year = today.year
            registrations = registrations.filter(
                user=request.user,
                date__year=year,
                date__month=month
            ).order_by('-date')

            context['calendar'] = mark_safe(
                RegistrationCalendar(registrations).formatmonth(
                    int(year), int(month)
                )
            )

        context['registrations'] = registrations

        if request.method == "POST":
            form = TimeRegForm(request.POST, user=request.user)
            if form.is_valid():
                timeregistration = form.save(commit=False)
                timeregistration.user = request.user
                timeregistration.week = form.cleaned_data[
                    'date'].isocalendar()[1]
                timeregistration.project = form.cleaned_data['project']
                project_phase_id = str(request.POST['project_phase'])
                if project_phase_id:
                    timeregistration.project_phase = Project_phase.objects.get(
                        pk=project_phase_id
                    )
                timeregistration.save()
                messages.success(request,
                                 'Successfully added {} hours on {}'.format(
                                     timeregistration.hours,
                                     timeregistration.date
                                 ))
                return redirect('/')
        else:
            form = TimeRegForm(user=request.user)

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
            firstname = profile_form.cleaned_data['first_name']
            lastname = profile_form.cleaned_data['last_name']

            # Create user object
            user = User.objects.create_user(username=username,
                                            first_name=firstname,
                                            last_name=lastname,
                                            email=email,
                                            password=password
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

    context['active_users'] = Profile.objects.filter(user__is_active=True)
    context['disabled_users'] = Profile.objects.filter(user__is_active=False)
    context['users'] = Profile.objects.filter(user__is_active=True)

    return render_to_response('tools_users.html',
                              RequestContext(request, context))


def disable_user(request):
    username = request.GET['user']
    user = User.objects.get(username=username)
    user.is_active = False
    user.save()
    messages.success(request, 'Successfully disabled user {}'.format(
        username))

    return redirect('/tools/users/')


def reenable_user(request):
    username = request.GET['user']
    user = User.objects.get(username=username)
    user.is_active = True
    user.save()
    messages.success(request, 'Successfully re-enabled user {}'.format(
        username))
    return redirect('/tools/users')


def do_undo_admin(request):
    username = request.GET['user']
    user = User.objects.get(username=username)

    if 'do' in request.GET:
        user.is_superuser = True
        messages.success(request, 'Successfully made {} administrator'.format(
            username))
    elif 'undo' in request.GET:
        user.is_superuser = False
        messages.success(request,
                         'Successfully removed {} as administrator'.format(
                             username)
                         )

    user.save()

    return redirect('/tools/users/')


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
        new_project = 'newProject' in request.POST
        new_phase = 'newPhase' in request.POST

        form = ProjectRegForm(request.POST)
        createProjectPhaseForm = ProjectPhaseCreateForm(request.POST)

        if new_project:
            if form.is_valid():
                project = form.save(commit=False)
                project.project_id = next_project_id() + 1
                project.is_active = True
                project.save()
                form.save_m2m()
                messages.success(
                    request,
                    'Successfully added project {}'.format(project.name)
                )
                return redirect('/tools/projects/')

        if new_phase:
            if createProjectPhaseForm.is_valid():
                projectPhase = createProjectPhaseForm.save(commit=False)
                projectPhase.is_active = True
                projectPhase.save()
                createProjectPhaseForm.save_m2m()
                messages.success(
                    request,
                    'Successfully added project phase {}'.format(
                        projectPhase.name
                    )
                )
                return redirect('/tools/projects/')
    else:
        form = ProjectRegForm()
        createProjectPhaseForm = ProjectPhaseCreateForm()

    context['project_form'] = form
    context['project_phase_form'] = createProjectPhaseForm

    active_projects = projects.filter(is_active=True).order_by('project_id')
    context['active_projects'] = active_projects

    closed_projects = projects.filter(is_active=False).order_by('project_id')
    context['closed_projects'] = closed_projects

    return render_to_response('tools_projects.html',
                              RequestContext(request, context))


def close_project(request):
    project_id = request.GET['project_id']
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


def open_project_phase(request):
    phase_pk = request.GET['phase_pk']
    Project_phase.objects.filter(pk=phase_pk).update(is_active=True)
    messages.success(request, 'Successfully reopened project phase #{}'.format(
        phase_pk))

    return redirect('/tools/projects/')


def close_project_phase(request):
    phase_pk = request.GET['phase_pk']
    Project_phase.objects.filter(pk=phase_pk).update(is_active=False)
    messages.success(request, 'Successfully closed project phase #{}'.format(
        phase_pk))

    return redirect('/tools/projects/')


def remove_registration(request, timereg_id):
    TimeRegistration.objects.filter(id=timereg_id).delete()
    messages.success(request, 'Successfully removed registration')

    return redirect('/')


def parse_ics(ics_file, project, user):
    if project is None:
        projects = Project.objects.filter().order_by('project_id')

        def next_project_id():
            current_id = projects.aggregate(Max(
                'project_id'))['project_id__max']
            if current_id is None:
                return 0
            else:
                return current_id

        project_name = ics_file.name.split('.')
        project = Project.objects.create(name="{}".format(project_name[0]),
                                         project_id=next_project_id() + 1)
        project.users.add(user)
        project.save()
    else:
        project = project

    # Try parsing the ics file. Will only parse events which arent all-day.
    try:
        cal = Calendar.from_ical(ics_file.read())
        for entry in cal.walk():
            if entry.name == 'VEVENT':
                start = entry.get('dtstart').dt
                end = entry.get('dtend').dt
                tdelta = end - start
                registration = TimeRegistration.objects.create(
                    user=user,
                    date=start,
                    week=start.isocalendar()[1],
                    start_time=start.time(),
                    end_time=end.time(),
                    hours=(tdelta.total_seconds() / 60.0) / 60.0,
                    project=project
                )
                registration.save()
    except AttributeError as e:
        print e


def show_profile(request):
    context = {}
    user = request.user

    context['username'] = user.username
    context['firstname'] = user.first_name
    context['lastname'] = user.last_name
    context['email'] = user.email

    if request.method == 'POST':
        if 'password' in request:
            user = User.objects.get(username=user.username)
            user.set_password(request.POST['password'])
            user.save()
            messages.success(request, 'Successfully changed password.')

        form = UploadIcsForm(request.POST, request.FILES)
        if form.is_valid():
            ics_file = request.FILES['ics_file']
            project = form.cleaned_data['projects']

            try:
                parse_ics(ics_file, project, user)
            except ValueError:
                raise ValidationError('Not an ics file.')

            messages.success(request, 'Successfully imported registrations.')
            return redirect('/profile/')

    else:
        form = UploadIcsForm()

    context['form'] = form

    return render_to_response('profile.html', RequestContext(request, context))
