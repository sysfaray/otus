from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user class
class User(AbstractUser):
    username = models.CharField(max_length=200, null=True, blank=True, unique=True)
    email = models.EmailField(max_length=200, null=True, blank=True, default='', unique=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars/')
    reg_date = models.DateField(null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


