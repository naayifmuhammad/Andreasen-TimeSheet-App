from django.contrib import admin

# Register your models here.
from .models import Project, Timesheet

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('employee', 'project', 'date', 'hours_worked')
    search_fields = ('employee__username', 'project__name')
    list_filter = ('date', 'project')