from typing import Any
from django import forms 
from .models import Timesheet, Project, Team
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone


class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['date', 'hours_worked', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date','class':'form-control smaller','value': timezone.now().date()}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'hours_worked': forms.NumberInput(attrs={'type':'number','class':'form-control smaller'})
        }

class ProjectForm(forms.ModelForm):
    team = forms.ModelChoiceField(queryset=Team.objects.all(),
                                  widget=forms.Select(
                                      attrs={'class' : 'form-control option-background'}
                                  ),
                                  empty_label='Assign to a team'
                                  )
    class Meta:
        model = Project
        fields = ['code', 'name', 'description', 'start_date', 'end_date','team']
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
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
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