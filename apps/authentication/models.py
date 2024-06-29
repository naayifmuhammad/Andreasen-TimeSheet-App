from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.home.models import Team

class CustomUser(AbstractUser):
    team = models.ForeignKey(Team,on_delete=models.SET_NULL,null=True,blank=True)