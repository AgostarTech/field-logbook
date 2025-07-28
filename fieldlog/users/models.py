# models.py (Refactored & Annotated)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

# -------------------------------
# Department & Course Models
# -------------------------------

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# -------------------------------
# Custom User Model
# -------------------------------
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
        'Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username

# -------------------------------
# Supervisor Profiles
# -------------------------------
class SupervisorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='supervisor_profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username

class OnStationSupervisor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='onstation_profile')
    company_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class OnCampusSupervisor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='oncampus_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

# -------------------------------
# Student Profile
# -------------------------------
class StudentProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    registration_number = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    year_of_study = models.PositiveSmallIntegerField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    institution_name = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    general_report = models.FileField(upload_to='reports/general/', blank=True, null=True)
    technical_report = models.FileField(upload_to='reports/technical/', blank=True, null=True)
    marks = models.FloatField(blank=True, null=True)
    supervisor_onstation = models.ForeignKey(OnStationSupervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name='onstation_students')
    supervisor_oncampus = models.ForeignKey(OnCampusSupervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name='oncampus_students')

    def __str__(self):
        return self.registration_number

# -------------------------------
# LogEntry for Student Daily Logs
# -------------------------------
class LogEntry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='log_entries')
    date = models.DateField(default=timezone.now, db_index=True)
    content = models.TextField()
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_logs')
    approved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', db_index=True)
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Log by {self.student.user.username} on {self.date} [{self.status}]"

    @property
    def is_approved(self):
        return self.status == 'approved'

    def approve(self, user):
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_by', 'approved_at'])

    def reject(self, user, reason=None):
        self.status = 'rejected'
        self.approved_by = user
        self.approved_at = timezone.now()
        if reason:
            self.rejection_reason = reason
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'rejection_reason'])

# -------------------------------
# AssignedTask Model
# -------------------------------
class AssignedTask(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]
    supervisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks_assigned')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='tasks_received')
    task_title = models.CharField(max_length=255)
    task_description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.task_title} for {self.student.user.username}"

# -------------------------------
# SupervisorUpload Model
# -------------------------------
class SupervisorUpload(models.Model):
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploads')
    file = models.FileField(upload_to='resources/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# -------------------------------
# Task (Many-to-Many)
# -------------------------------
class Task(models.Model):
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks_created')
    assigned_to = models.ManyToManyField(StudentProfile, related_name='tasks_received_m2m')
    description = models.TextField()
    completed = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Task {self.id} by {self.assigned_by.username}"

# -------------------------------
# TaskResource
# -------------------------------
class TaskResource(models.Model):
    TYPE_CHOICES = (
        ('Task', 'Task'),
        ('Resource', 'Resource'),
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    )

    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    deadline = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(CustomUser, blank=True)
    access_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def assigned_to_names(self):
        return ", ".join([user.get_full_name() for user in self.assigned_to.all()])

    def __str__(self):
        return self.title

# -------------------------------
# UploadedDocument Model
# -------------------------------
class UploadedDocument(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='uploaded_documents')
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='uploaded_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Document {self.pk}"

# -------------------------------
# Evaluation Form Model
# -------------------------------
class EvaluationForm(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    strengths = models.TextField()
    benefits_personal = models.TextField()
    org_benefits = models.TextField()
    community_benefits = models.TextField()
    relevance = models.TextField()
    constraint = models.TextField()
    solution = models.TextField()
    suggestions = models.TextField()
    knowledge = models.TextField()
    skills = models.TextField()
    supervision = models.TextField()
    evaluation_method = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation by {self.student.user.username} on {self.submitted_at.strftime('%Y-%m-%d') }"

# -------------------------------
# DepartmentResource Model
# -------------------------------
class DepartmentResource(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='department_resources/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# -------------------------------
# Organization Model
# -------------------------------
class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or "Unnamed Organization"
