from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from users.models import CustomUser  # Ensure CustomUser is defined in users/models.py

# ========================
# Place & Institution
# ========================

class Place(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Institution(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='institutions')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.place.name})"


# ========================
# Supervisor Profile
# ========================

class SupervisorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='logbook_supervisorprofile')

    def __str__(self):
        return self.user.username

from django.db import models
from django.conf import settings
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver


# ========================
# Student Profile
# ========================

class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    registration_number = models.CharField(max_length=30, unique=True)
    course = models.CharField(max_length=100)
    year_of_study = models.PositiveSmallIntegerField()
    academic_year = models.CharField(max_length=20, default='2024/2025')
    field_start_date = models.DateField(default=date.today, null=True, blank=True)
    organization_name = models.CharField(max_length=255, blank=True, null=True)

    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_students'
    )

    def __str__(self):
        return self.user.username


# Signal to create StudentProfile when a new user with role 'student' is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    if created and getattr(instance, 'role', None) == 'student':
        # Provide default values for required fields to avoid NOT NULL errors
        StudentProfile.objects.create(
            user=instance,
            year_of_study=1,                         # Default year of study
            registration_number=f"TEMP{instance.pk}",  # Temporary unique reg number
            course="Unknown",                        # Temporary course name
        )

# ========================
# Logbook Entry
# ========================

class LogEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='log_entries')
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True, related_name='log_entries')
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True, related_name='log_entries')
    date = models.DateField()
    day_number = models.PositiveIntegerField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    description = models.TextField()
    trainee_signature = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

        


# ========================
# Uploaded Files
# ========================

class UploadedFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"


# ========================
# Weekly Progress Report
# ========================

class ProgressReport(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress_reports')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_reports')
    week_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    supervisor_comment = models.TextField(blank=True)
    onstation_supervisor_comment = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'week_number')
        ordering = ['week_number']

    def __str__(self):
        return f"Week {self.week_number} - {self.student.username}"


# ========================
# Task Model
# ========================

class Task(models.Model):
    description = models.TextField()
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks_assigned')
    assigned_to = models.ManyToManyField(StudentProfile, related_name='tasks_received')
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Task by {self.assigned_by.username} at {self.assigned_at.strftime('%Y-%m-%d %H:%M')}"
