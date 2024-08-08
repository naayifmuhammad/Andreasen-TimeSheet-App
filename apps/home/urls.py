
from django.urls import path, re_path
from apps.home import views
from django.contrib import admin


urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('create_project/', views.create_project, name='create_project'),  # URL for creating a new project
    path('add-customer/', views.add_customer, name='add_customer'),
    path('add-team/', views.add_team, name='add_team'),
    #path('create_timesheet/', views.create_timesheet, name='create_timesheet'),  # URL for creating a timesheet
    path('projects/', views.projects_tab, name='projects_tab'),
    
    path('old_projects/', views.old_projects, name='old_projects'),

    path('manage_projects/', views.manage_projects, name='manage_projects'),
    path('toggle_project_status/<int:project_id>/', views.toggle_project_status, name='toggle_project_status'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('project/edit/<int:project_id>/', views.edit_project, name='edit_project'),

    path('make_admin/<int:employee_id>/', views.make_admin, name='make_admin'),
    
    path('active_projects/', views.timesheet, name='timesheet'),  # URL for timesheet page
    path('timesheet_entry/<int:project_id>/', views.timesheet_entry, name='timesheet_entry'),
    path('project_details/<int:project_id>/', views.project_details, name='project_details'),
    path('add_timesheet_entry/<int:project_id>/', views.add_timesheet_entry, name='add_timesheet_entry'),
    path('bi-weekly/', views.view_weekly_timesheet, name='view_weekly_timesheet'),
    path('export-timesheet/<str:start_date>/<str:end_date>/', views.export_timesheet, name='export_timesheet'),
    #path for the button to export the project based timesheet
    path('export_project_based_timesheet_summary/<int:project_id>', views.export_project_based_timesheet_summary, name='export_project_based_timesheet_summary'),
    #path for the button to export the employee report
    path('print_employee_report/', views.print_employee_report, name='print_employee_report'),

    
    path('update-username/', views.update_username, name='update_username'),
    path('update-password/', views.update_password, name='update_password'),
    path('update-email/', views.update_email, name='update_email'),

    path('profile',views.view_profile ,name='profile'),
    path('manage_employees/', views.manage_employees, name='manage_employees'),
    path('manage_employees/add/', views.add_employee, name='add_employee'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('delete_timesheet/<int:timesheet_id>/', views.delete_timesheet, name='delete_timesheet'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
