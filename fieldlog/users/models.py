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


# Supervisor Profile (generic)
class SupervisorProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='supervisor_profile'
    )
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username


# On-Station Supervisor Profile
class OnStationSupervisor(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='onstation_profile'
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
        related_name='oncampus_profile'
    )
    department = models.CharField(max_length=100, blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Student Profile
class StudentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_profiles'
    )
    registration_number = models.CharField(max_length=50, unique=True)
    course = models.CharField(max_length=100)
    year_of_study = models.PositiveSmallIntegerField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    institution_name = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    supervisor_onstation = models.ForeignKey(
        OnStationSupervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='onstation_students'
    )
    supervisor_oncampus = models.ForeignKey(
        OnCampusSupervisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='oncampus_students'
    )

    def __str__(self):
        return self.registration_number


# Log Entry
class LogEntry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
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
        related_name='approved_logs'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.student.user.username} | {self.date}"


# Assigned Tasks by Supervisor
class AssignedTask(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    supervisor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='tasks_assigned'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='tasks_received'
    )
    task_title = models.CharField(max_length=255)
    task_description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.task_title} for {self.student.user.username}"


# Supervisor Upload Files
class SupervisorUpload(models.Model):
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='uploads'
    )
    file = models.FileField(upload_to='resources/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Optional Task model with ManyToMany to Students (if you want)
class Task(models.Model):
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='tasks_created'
    )
    assigned_to = models.ManyToManyField(StudentProfile, related_name='tasks_received_m2m')
    description = models.TextField()
    completed = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Task {self.id} by {self.assigned_by.username}"
