from django import template
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib import messages
from django.urls import reverse
from .forms import TimesheetForm, ProjectForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Project, Timesheet
from django.db.models import Sum
from django.utils.timezone import now
from django.contrib.auth.models import User


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


@login_required(login_url="/login/")
def timesheet(request):
    active_projects = Project.objects.filter(is_active=True)
    context = {
        'active_projects': active_projects
    }
    return render(request, 'home/timesheet.html', context)

@login_required(login_url="/login/")
def project_details(request,project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    if request.user.is_staff:
        # If user is staff, fetch total hours worked by all employees on this project
        timesheets = Timesheet.objects.filter(project=project).order_by('date')
        total_time = timesheets.aggregate(total_time=Sum('hours_worked'))['total_time'] or 0
        timesheetcount = timesheets.count()
        timesheets = timesheets.select_related('employee').order_by('date')  
    else:
        # If user is not staff, fetch timesheets added by the current user only
        timesheets = Timesheet.objects.filter(project=project, employee=request.user).order_by('date')
        total_time = timesheets.aggregate(total_time=Sum('hours_worked'))['total_time'] or 0
        timesheetcount = timesheets.count()

    context = {
        'project': project,
        'timesheets': timesheets,
        'total_time': total_time,
        'timesheetcount':timesheetcount,
    }
    return render(request, 'home/project_details.html', context)
    
    
    
    
    
    # timesheets = Timesheet.objects.filter(project=project).order_by('date')  # Assuming 'date' field for chronological order
    # total_time = timesheets.aggregate(total_time=Sum('hours_worked'))['total_time'] or 0
    # update_count = timesheets.count()
    # context = {
    #     'project' : project,
    #     'timesheets' : timesheets,
    #     'total_time' : total_time,
    #     'update_count' : update_count,
    # }
    # return render(request,'home/project_details.html',context)


@login_required(login_url="/login/")
def projects_tab(request):
    active_projects = Project.objects.filter(is_active=True)
    
    inactive_projects = Project.objects.filter(is_active=False)

    active_project_count = active_projects.count()
    inactive_project_count = inactive_projects.count()
    context = {
        'active_projects': active_projects,
        'active_project_count': active_project_count,
        'inactive_project_count' : inactive_project_count,
    }
    if request.user.is_staff:
        print("is admin")
        return render(request, 'home/admin/admin_projects.html', context)
    else:
        print("Regular user")
        return render(request, 'home/projects.html', context)



@login_required(login_url="/login/")
def old_projects(request):
    
    inactive_projects = Project.objects.filter(is_active=False)
    inactive_project_count = inactive_projects.count()

    context = {
        'inactive_projects': inactive_projects,    
        'inactive_project_count' : inactive_project_count,
    }
    return render(request, 'home/old-projects.html', context)


@login_required(login_url="/login/")
def manage_projects(request):
    
    projects = Project.objects.all()
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
    print(project.name, " ", project.is_active)
    project.is_active = not project.is_active
    project.save()
    return redirect("manage_projects")


@login_required(login_url="/login/")
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect('projects_tab')  # Redirect to a success page or another view
    else:
        form = ProjectForm()
        return render(request, 'home/new-project.html', {'form': form})


@login_required(login_url="/login/")
def timesheet_entry(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    form = TimesheetForm()
    
    return render(request, 'home/new-timesheet-entry.html', {'form': form, 'project': project})


@login_required(login_url="/login/")
def view_profile(request):
    return render(request, 'home/user.html')


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
            return redirect('timesheet')  # Redirect to 'timesheet' view after saving timesheet
        else:
            messages.error(request, 'Error submitting timesheet. Please correct the form errors.')  # Error message
            print(form.errors)  # Print form errors to console for debugging
    else:
        form = TimesheetForm()

    return render(request, 'home/new-timesheet-entry.html', {'form': form, 'project_name': project_name, 'project': project})




#account update related operations:
@login_required
def update_details(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        user = request.user

        # Update username if provided
        if username:
            user.username = username

        # Update password if provided
        if password:
            user.set_password(password)

        # Update email if provided
        if email:
            user.email = email

        # Save the updated user object
        user.save()

        messages.success(request, 'Your details have been updated successfully.')
        return redirect('profile')  
    
    return render(request, 'user.html')  


@login_required(login_url="/login/")
def manage_employees(request):
    all = User.objects.exclude(id=request.user.id).all()
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
    print("request: ",request.user.id,"id : ",employee.id)
    if request.user.id == employee.id:
        return redirect("/login/")
    return redirect("manage_employees")


from .forms import EmployeeCreationForm

@login_required(login_url="/login/")
def add_employee(request):
    if not request.user.is_staff:
        return redirect('home')  # Non-staff users cannot access this view

    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_employees')  # Redirect to the employee list or another appropriate page
    else:
        form = EmployeeCreationForm()
    
    return render(request, 'home/admin/add_employee.html', {'form': form})
