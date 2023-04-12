from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=150)
    username = models.CharField(max_length=50)
    confirm_password = models.CharField(max_length=50)
    #gender = models.CharField(max_length=10)
    age = models.CharField(max_length=3)
    phone_number = models.CharField(unique=True, max_length=20)
    #location = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name', 'username', 'age', ]
    
    def __str__(self):
        return self.username