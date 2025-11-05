from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(models.Model):
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)

is_coach = models.BooleanField(default=False)
def __str__(self):
return self.username