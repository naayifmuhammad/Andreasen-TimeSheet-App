
from django.urls import path, re_path
from apps.home import views
from django.contrib import admin


urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('create_project/', views.create_project, name='create_project'),  # URL for creating a new project
    #path('create_timesheet/', views.create_timesheet, name='create_timesheet'),  # URL for creating a timesheet
    path('projects/', views.projects_tab, name='projects_tab'),
    
    path('old_projects/', views.old_projects, name='old_projects'),

    path('manage_projects/', views.manage_projects, name='manage_projects'),
    path('toggle_project_status/<int:project_id>/', views.toggle_project_status, name='toggle_project_status'),
    path('make_admin/<int:employee_id>/', views.make_admin, name='make_admin'),



    path('active_projects/', views.timesheet, name='timesheet'),  # URL for timesheet page
    path('timesheet_entry/<int:project_id>/', views.timesheet_entry, name='timesheet_entry'),
    path('project_details/<int:project_id>/', views.project_details, name='project_details'),
    path('add_timesheet_entry/<int:project_id>/', views.add_timesheet_entry, name='add_timesheet_entry'),
    path('update_details/', views.update_details, name='update_details'),
    path('profile',views.view_profile ,name='profile'),
    path('manage_employees/', views.manage_employees, name='manage_employees'),
    path('manage_employees/add/', views.add_employee, name='add_employee'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
