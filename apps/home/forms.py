from typing import Any
from django import forms 
from .models import Timesheet, Project, Team, Customer
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.core.validators import MaxValueValidator
from apps.authentication.models import CustomUser
from .date_fetcher import fetchWeekDropdown

class TimesheetForm(forms.ModelForm):
    # date = forms.ChoiceField(
    #     choices=[],
    #     widget=forms.Select(
    #         attrs={'class': ''}
    #     ),
    #     label='Choose day'
    # )

    # def __init__(self, *args, **kwargs):
    #     week_choices = kwargs.pop('week_choices', [])
    #     super().__init__(*args, **kwargs)
    #     self.fields['date'].choices = week_choices

    class Meta:
        model = Timesheet
        fields = ['hours_worked', 'description']
        validators = [MaxValueValidator(24)]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            #'hours_worked': forms.NumberInput(attrs={'type': 'number', 'class': 'form-control smaller'}),
            'hours_worked': forms.NumberInput(attrs={'class': 'form-control smaller', 'step': '0.1'}),
        }

class ProjectForm(forms.ModelForm):
    team = forms.ModelChoiceField(queryset=Team.objects.all(),
                                  widget=forms.Select(
                                      attrs={'class' : 'form-control option-background', "id" : 'team-select'}
                                  ),
                                  empty_label='Assign to a team'
                                  )
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control option-background', 'id': 'customer-select'}
        ),
        empty_label='Select a customer'
    )
    class Meta:
        model = Project
        fields = ['code', 'name', 'description', 'start_date', 'end_date','team','customer']
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'ff-NNNN', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'start_date': forms.DateInput(attrs={'type': 'date','value': timezone.now().date(), 'class': 'form-control'}, format='%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].input_formats = ['%Y-%m-%d']
        self.fields['end_date'].input_formats = ['%Y-%m-%d']
        if not self.user.is_superuser:
            self.fields['team'].queryset = Team.objects.filter(id=self.user.team.id)
        else:
            self.fields['team'].queryset = Team.objects.all()


class EditProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['code', 'name', 'description', 'start_date', 'end_date']
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'ff-NNNN', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
        }
        
    
    def __init__(self, *args, **kwargs):
        super(EditProjectForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].input_formats = ['%Y-%m-%d']
        self.fields['end_date'].input_formats = ['%Y-%m-%d']
        for field in self.fields.values():
            field.required = False


class EmployeeCreationForm(UserCreationForm):
    class Meta:
       model = CustomUser
       fields = ('username','first_name' ,'last_name', 'email', 'password1', 'password2', 'team')
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter first name",
                "class": "form-control"
            }
        ))
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter last name",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))
    team = forms.ModelChoiceField(queryset=Team.objects.all(),
                                  widget=forms.Select(
                                      attrs={'class' : 'form-control option-background'}
                                  ),
                                  empty_label='Assign to a team'
                                  )
    
    

    def __init__(self, *args, **kwargs):
       self.user = kwargs.pop('user',None)
       super().__init__(*args, **kwargs)
       if self.user and not self.user.is_superuser:
        # Update queryset based on user's team
        self.fields['team'].queryset = Team.objects.filter(id=self.user.team.id)




    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.team = self.cleaned_data['team']
        if commit:
            user.save()
            print("User's team = ",user.team)
        return user