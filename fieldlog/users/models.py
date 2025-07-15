from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# ==========================
# Custom User Model
# ==========================
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('onstation', 'Onstation Supervisor'),
        ('oncampus', 'On-campus Supervisor'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username

# ==========================
# Student Profile
# ==========================
class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='studentprofile'
    )
    registration_number = models.CharField(max_length=30, unique=True)
    course = models.CharField(max_length=100)
    year_of_study = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.registration_number}"

# ==========================
# Supervisor Profile
# ==========================
class SupervisorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='supervisorprofile'
    )
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.department}"
