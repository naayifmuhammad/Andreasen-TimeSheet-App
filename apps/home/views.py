from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib import messages
from django.urls import reverse
from .forms import TimesheetForm, ProjectForm, EditProjectForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Timesheet, Team
from django.db.models import Sum
from django.utils.timezone import now
from .forms import EmployeeCreationForm
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.authentication.models import CustomUser as User
from .date_fetcher import *
from django.http import HttpResponse
from datetime import datetime
from django.http import HttpResponse
import csv
from .utils import generate_project_report, generate_employee_report, getBiWeeklyRanges, generate_week_ranges_from_given_startdate_till_date, generate_employee_report



@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/projects.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


#obselete
@login_required(login_url="/login/")
def create_timesheet(request):
    if request.method == 'POST':
        form = TimesheetForm(request.POST)
        if form.is_valid():
            timesheet = form.save(commit=False)
            timesheet.employee = request.user
            timesheet.save()
            return redirect('timesheet_success')  # Redirect to a success page or another view
    else:
        form = TimesheetForm()
    return render(request, 'home/timesheet.html', {'form': form})



#latest - to export project based timesheet. triggered from project details page of admin
@login_required(login_url="/login/")
def export_project_based_timesheet_summary(request,project_id=None, start_date=None,end_date=None):

    start_date = datetime.strptime(request.GET.get('start_date'),'%d/%m/%Y').date()
    end_date = datetime.strptime(request.GET.get('end_date'), '%d/%m/%Y').date()

    project = get_object_or_404(Project, pk=project_id)
    
    week_ranges = generate_week_ranges_from_given_startdate_till_date(start_date,end_date)


    if request.user.is_staff:
        previous_week_timesheets =  Timesheet.objects.filter(project=project_id , date__range=(week_ranges[0]['start'].strftime("%Y-%m-%d"),week_ranges[0]['end'].strftime("%Y-%m-%d"))).order_by('date')
        current_week_timesheets =  Timesheet.objects.filter(project=project_id , date__range=(week_ranges[1]['start'].strftime("%Y-%m-%d"),week_ranges[1]['end'].strftime("%Y-%m-%d"))).order_by('date') 
        previous_week_total_time_worked = current_week_total_time_worked = 0
        if previous_week_timesheets:
            previous_week_total_time_worked = previous_week_timesheets.aggregate(p_total_hours=Sum('hours_worked'))['p_total_hours']
            
        if current_week_timesheets:
            current_week_total_time_worked = current_week_timesheets.aggregate(c_total_hours=Sum('hours_worked'))['c_total_hours']    

    context = {
    'project' : project,
    'timesheets' : {'previous' : previous_week_timesheets, 'current': current_week_timesheets},
    'duration' : {'pStart' : week_ranges[0]['start'].strftime('%d-%m-%y'), 'pEnd' : week_ranges[0]['end'].strftime('%d-%m-%y'), 'cStart':week_ranges[1]['start'].strftime('%d-%m-%y'), 'cEnd': week_ranges[1]['end'].strftime('%d-%m-%y')},
    'total' : {'previous' : previous_week_total_time_worked, 'current': current_week_total_time_worked}
    }
    filename = f"report-({start_date.strftime('%d-%m-%y')}-to{end_date.strftime('%d-%m-%y')}).pdf"
    
    return generate_project_report(filename,**context)


@login_required(login_url="/login/")
def view_weekly_timesheet(request, pStart=None,pEnd=None, cStart=None, cEnd=None):
    
    fetchedTimePeriods = getTimePeriods()
    if not pStart:
        pStart = fetchedTimePeriods['pStart']

    if not pEnd:
        pEnd = fetchedTimePeriods['pEnd']
    if not cStart:
        cStart = fetchedTimePeriods['cStart']

    if not cEnd:
        cEnd = fetchedTimePeriods['cEnd']
 

    employees = []
    if request.user.is_superuser:
        employees = User.objects.exclude(is_superuser=True)
        if request.GET.get('employee_id'):
            employee_id = request.GET.get('employee_id')
        else:
            employee_id = employees[0]
        previous_week_timesheets = Timesheet.objects.filter(employee=employee_id,date__range=(pStart.strftime("%Y-%m-%d"),pEnd.strftime("%Y-%m-%d"))).order_by('date') 
        current_week_timesheets = Timesheet.objects.filter(employee=employee_id, date__range=(cStart.strftime("%Y-%m-%d"),cEnd.strftime("%Y-%m-%d"))).order_by('date') 
    elif request.user.is_staff:
        employees = User.objects.filter(team=request.user.team).exclude(is_staff=True)
        if request.GET.get('employee_id'):
            employee_id = request.GET.get('employee_id')
        else:
            employee_id = employees[0]
        previous_week_timesheets = Timesheet.objects.filter(employee=employee_id, project__team=request.user.team,date__range=(pStart.strftime("%Y-%m-%d"),pEnd.strftime("%Y-%m-%d"))).order_by('date') 
        current_week_timesheets = Timesheet.objects.filter(employee=employee_id, project__team=request.user.team,date__range=(cStart.strftime("%Y-%m-%d"),cEnd.strftime("%Y-%m-%d"))).order_by('date') 
  
    for timesheet in previous_week_timesheets:
        timesheet.day = timesheet.date.strftime("%A")
    for timesheet in current_week_timesheets:
        timesheet.day = timesheet.date.strftime("%A")


    active_projects = Project.objects.filter(is_active=True, team=request.user.team)
    context = {
        'active_projects': active_projects,
        'timesheets' : [previous_week_timesheets, current_week_timesheets],
        'duration' : {'start': pStart.strftime('%d-%m-%y'),'end' : cEnd.strftime('%d-%m-%y')},
        'employees' : employees,
    }
    return render(request, 'home/bi-weekly_timesheet.html', context)

#creates data for the pdf export for employee report PDF
@login_required(login_url="/login/")
def print_employee_report(request, pStart=None,pEnd=None, cStart=None, cEnd=None):
    
    employee_model = get_user_model()
    employee_id = request.GET.get('employee_id')
    employee = get_object_or_404(employee_model, id=employee_id)
    fetchedTimePeriods = getTimePeriods()
    if not pStart:
        pStart = fetchedTimePeriods['pStart']

    if not pEnd:
        pEnd = fetchedTimePeriods['pEnd']
    if not cStart:
        cStart = fetchedTimePeriods['cStart']

    if not cEnd:
        cEnd = fetchedTimePeriods['cEnd']
    
    if request.user.is_superuser or request.user.is_staff: 
        previous_week_timesheets = Timesheet.objects.filter(employee=employee, date__range=(pStart.strftime("%Y-%m-%d"),pEnd.strftime("%Y-%m-%d"))).order_by('date')
        current_week_timesheets = Timesheet.objects.filter(employee=employee, date__range=(cStart.strftime("%Y-%m-%d"),cEnd.strftime("%Y-%m-%d"))).order_by('date')

    for timesheet in previous_week_timesheets:
        timesheet.day = timesheet.date.strftime("%A")
    for timesheet in current_week_timesheets:
        timesheet.day = timesheet.date.strftime("%A")

    duration = {'start': pStart.strftime('%d-%m-%y'),'end' : cEnd.strftime('%d-%m-%y')}
    filename = f"{employee.name}-{duration['start']}-to-{duration['end']}-report.pdf"
    timesheets= [previous_week_timesheets, current_week_timesheets],
    filename = duration['start']
    return generate_employee_report(employee,timesheets, filename, duration)


@login_required(login_url="/login/")
def timesheet(request):
    active_projects = Project.objects.filter(is_active=True, team=request.user.team)
    context = {
        'active_projects': active_projects
    }
    return render(request, 'home/timesheet.html', context)


@login_required(login_url="/login/")



#we don't need csv anymore
def export_timesheet(request, start_date, end_date):

    start_date = datetime.strptime(start_date, "%d-%m-%y")
    end_date = datetime.strptime(end_date, "%d-%m-%y") + timedelta(days=1)  # Adjust end date to be inclusive
    timesheets = Timesheet.objects.filter(date__range=(start_date, end_date)).order_by('date')
    #test
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="timesheet_export_{start_date.strftime("%d-%m-%y")} - {end_date.strftime("%d-%m-%y")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Project ID', 'Project Name', 'Description of work', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri'])


    for timesheet in timesheets:
        project_id = timesheet.project.code
        project_name = timesheet.project.name
        description = timesheet.description
        Monday = timesheet.hours_worked if timesheet.date.strftime("%A") == "Monday" else 0
        Tuesday = timesheet.hours_worked if timesheet.date.strftime("%A") == "Tuesday" else 0
        Wednesday = timesheet.hours_worked if timesheet.date.strftime("%A") == "Wednesday" else 0
        Thursday = timesheet.hours_worked if timesheet.date.strftime("%A") == "Thursday" else 0
        Friday = timesheet.hours_worked if timesheet.date.strftime("%A") == "Friday" else 0
        writer.writerow([project_id, project_name, description, Monday, Tuesday,Wednesday,Thursday,Friday])
    return response




@login_required(login_url="/login/")
def project_details(request,project_id):
    project = get_object_or_404(Project, pk=project_id)
    individual_time_sheet_data = dict()

    exclusive_staff_data = dict()

    if request.user.is_staff:
        # If user is staff, fetch total hours worked by all employees on this project
        timesheets = Timesheet.objects.filter(project=project).order_by('date')
        total_time = timesheets.aggregate(total_time=Sum('hours_worked'))['total_time'] or 0
        
        exclusive_staff_data['total_timesheet_count'] = timesheets.count()
        
        timesheets = timesheets.select_related('employee').order_by('date')
        # Fetch distinct employees who have contributed to the project
        employee_ids = timesheets.values_list('employee_id', flat=True).distinct()
        employees = get_user_model().objects.filter(id__in=employee_ids)
        
        for employee in employees:
            timesheets_of_employee = timesheets.filter(employee = employee)
            timesheetcount = timesheets_of_employee.count()
            individual_time_sheet_data[employee] = {
                'timesheets' : timesheets_of_employee,
                'total_hours_worked' : timesheets_of_employee.aggregate(hours_worked = Sum('hours_worked'))['hours_worked'] or 0,
                'timesheetcount' : timesheetcount,
            }  
        exclusive_staff_data['individual_time_sheet_data'] = individual_time_sheet_data

    else:
        # If user is not staff, fetch timesheets added by the current user only
        timesheets = Timesheet.objects.filter(project=project, employee=request.user).order_by('date')
        total_time = timesheets.aggregate(total_time=Sum('hours_worked'))['total_time'] or 0
        timesheetcount = timesheets.count()

    context = {
        'project': project,
        'timesheets': timesheets,
        'total_time': total_time,
        'biweekly_ranges' : getBiWeeklyRanges(),
    }
    
    if request.user.is_staff: # only needed for staff
        context.update(exclusive_staff_data)
    else:
        context['timesheetcount'] = timesheetcount

    return render(request, 'home/project_details.html', context)


@login_required(login_url="/login/")
def projects_tab(request):
    if request.user.is_superuser:
        active_projects = Project.objects.filter(is_active=True).all()
        inactive_projects = Project.objects.filter(is_active=False).all()
        teams = Team.objects.all()
    else:
        active_projects = Project.objects.filter(team = request.user.team).filter(is_active = True)
        inactive_projects = Project.objects.filter(team = request.user.team).filter(is_active = False)
    
    

    active_project_count = active_projects.count()
    inactive_project_count = inactive_projects.count()
    context = {
        'active_projects': active_projects,
        'active_project_count': active_project_count,
        'inactive_project_count' : inactive_project_count,
    }
    if request.user.is_superuser:
        context['teams'] = teams

    return render(request, 'home/projects.html', context)



@login_required(login_url="/login/")
def old_projects(request):
    if request.user.is_superuser:
        inactive_projects = Project.objects.filter(is_active=False)
    else:
        inactive_projects = Project.objects.filter(team = request.user.team).filter(is_active = False)
    inactive_project_count = inactive_projects.count()

    context = {
        'inactive_projects': inactive_projects,    
        'inactive_project_count' : inactive_project_count,
    }
    return render(request, 'home/old-projects.html', context)


@login_required(login_url="/login/")
def manage_projects(request):
    
    projects = Project.objects.all() if request.user.is_superuser else Project.objects.filter(team = request.user.team)
    project_count = projects.count()
    active = projects.filter(is_active=True).count()
    inactive = projects.filter(is_active=False).count()
    context = {
        'projects': projects,    
        'project_count' : project_count,
        'active' : active,
        'inactive' : inactive,
    }
    return render(request, 'home/manage-projects.html', context)


@login_required(login_url="/login/")
def toggle_project_status(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.is_active = not project.is_active
    if not project.is_active and not project.end_date:
        project.end_date = timezone.now().date()
    else:
        project.end_date = None
    project.save()

    return redirect("manage_projects")


@login_required(login_url="/login/")
def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    return redirect("manage_projects")


@login_required(login_url="/login/")
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST,user=request.user)
        if form.is_valid():
            form.save()
            return redirect('projects_tab')  # Redirect to a success page or another view
    else:
        form = ProjectForm(user = request.user)
    return render(request, 'home/new-project.html', {'form': form})


@login_required(login_url="/login/")
def timesheet_entry(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    form = TimesheetForm()

    week_dates = get_current_week_dates()
    week = {
        'start' : week_dates[0],
        'end' : week_dates[-1],
    }


    context = {
        'form': form,
        'project' : project,
        'week' : week,
    }
    
    return render(request, 'home/new-timesheet-entry.html', context)


@login_required(login_url="/login/")
def view_profile(request):
    return render(request, 'home/user.html')

@login_required(login_url="/login/")
def delete_user(request, user_id):
    if request.user.is_staff:  #only admins can delete users
        user = get_object_or_404(User, id=user_id)    
        user.delete()
    return redirect('manage_employees')  


@login_required(login_url="/login/")
def delete_timesheet(request, timesheet_id):
    if not request.user.is_staff:  #only employees can do this
        timesheet = get_object_or_404(Timesheet, id=timesheet_id)    
        project = timesheet.project
        timesheet.delete()
        return redirect('project_details', project_id = project.id)
    return redirect('')  


@login_required(login_url="/login/")
def add_timesheet_entry(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project_name = project.name

    if request.method == 'POST':
        form = TimesheetForm(request.POST)
        if form.is_valid():
            timesheet = form.save(commit=False)
            timesheet.employee = request.user
            timesheet.project = project
            timesheet.save()
            messages.success(request, 'Timesheet entry created successfully.')  # Success message
            return redirect('project_details',project_id = project.id)  # Redirect to 'timesheet' view after saving timesheet
        else:
            messages.error(request, 'Error submitting timesheet. Please correct the form errors.')  # Error message
            print(form.errors)  # Print form errors to console for debugging
    else:
        form = TimesheetForm()

    return render(request, 'home/new-timesheet-entry.html', {'form': form, 'project_name': project_name, 'project': project})





#account related updates 
@login_required
def update_username(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            request.user.username = username
            request.user.save()
            messages.success(request, 'Username updated successfully.')
        return redirect('profile')  # Adjust the redirect URL as needed

@login_required
def update_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password:
            request.user.set_password(password)
            request.user.save()
            messages.success(request, 'Password updated successfully.')
        return redirect('profile')  # Adjust the redirect URL as needed

@login_required
def update_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            request.user.email = email
            request.user.save()
            messages.success(request, 'Email updated successfully.')
        return redirect('profile')  # Adjust the redirect URL as needed
    


#edit project details here
@login_required(login_url="/login/")
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = EditProjectForm(request.POST)
        if form.is_valid():
            for field, value in form.cleaned_data.items():
                if value is not None and value != '':
                    setattr(project,field,value)
            project.save()
            messages.success(request, 'Project Updated Successfully.')  # Success message
            msg = "Project Updated Successfully" 
            return render(request, 'home/edit_project.html', {'form': form, 'project': project, 'msg' : msg})
        else:
            messages.error(request, 'Error submitting the edit. Please correct the form errors.')  # Error message
            print(form.errors)  # Print form errors to console for debugging
    else:
        form = EditProjectForm()

    return render(request, 'home/edit_project.html', {'form': form, 'project': project})




@login_required(login_url="/login/")
def manage_employees(request):
    if request.user.is_superuser:
        all = User.objects.exclude(id=request.user.id).exclude(is_superuser = True).all()
    else:
        all = User.objects.exclude(id=request.user.id).exclude(is_superuser = True).filter(team=request.user.team).all()
    context = {
        'all' : all,
    }
    return render(request, 'home/admin/manage_employees.html', context)

@login_required(login_url="/login/")
def make_admin(request, employee_id):
    if not request.user.is_staff:
        return redirect("home")
    employee = get_object_or_404(User, pk=employee_id)
    employee.is_staff = not employee.is_staff
    employee.save()
    if request.user.id == employee.id:
        return redirect("/login/")
    return redirect("manage_employees")



@login_required(login_url="/login/")
def add_employee(request):
    if not request.user.is_staff:
        return redirect('home')  # Non-staff users cannot access this view

    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST,user=request.user)
        if form.is_valid():
            form.save()
            return redirect('manage_employees')  # Redirect to the employee list or another appropriate page
    else:
        form = EmployeeCreationForm(user=request.user)
    
    return render(request, 'home/admin/add_employee.html', {'form': form})


