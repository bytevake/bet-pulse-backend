from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    # profile_pic = models.ImageField(null=True)
    phone_no = models.CharField(unique=True, default="", max_length=20)
    username = models.CharField(unique=True, max_length=50)
    national_id = models.CharField(unique=True, max_length=50)
