from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Department model
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Custom user model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('onstation', 'On-Station Supervisor'),
        ('oncampus', 'On-Campus Supervisor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users'
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username


# Supervisor profile
class SupervisorProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='users_supervisor_profile'
    )
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Student profile
class StudentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='users_student_profile'
    )
    registration_number = models.CharField(max_length=30, unique=True)
    course = models.CharField(max_length=100)
    year_of_study = models.PositiveSmallIntegerField()
    supervisor_onstation = models.ForeignKey(
        SupervisorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='onstation_students'
    )
    supervisor_oncampus = models.ForeignKey(
        SupervisorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='oncampus_students'
    )

    def __str__(self):
        return f"{self.user.username} - {self.registration_number}"


# Log entry
class LogEntry(models.Model):
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name='log_entries'
    )
    date = models.DateField(default=timezone.now)
    content = models.TextField()
    approved_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="approved_logs"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"{self.student.user.username} | {self.date}"


# Assigned tasks by supervisor
class AssignedTask(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    supervisor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='users_tasks_assigned'
    )
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE, 
        related_name='users_tasks_received'
    )
    task_title = models.CharField(max_length=255)
    task_description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.task_title} for {self.student.user.username}"


# Supervisor upload files
class SupervisorUpload(models.Model):
    uploaded_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='users_uploads'
    )
    file = models.FileField(upload_to='resources/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# On-Station Supervisor Profile
class OnStationSupervisor(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='users_onstation_supervisor_profile'
    )
    company_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# On-Campus Supervisor Profile
class OnCampusSupervisor(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='users_oncampus_supervisor_profile'
    )
    department = models.CharField(max_length=100, blank=True, null=True)  # optional

    def __str__(self):
        return self.user.get_full_name() or self.user.username
