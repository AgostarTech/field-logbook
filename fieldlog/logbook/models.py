from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

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
        return f"{self.name} - {self.place.name}"


# ========================
# Supervisor Profile
# ========================

class SupervisorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='logbook_supervisor_profile'  # Changed related_name to avoid conflicts
    )
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# ========================
# Student Profile
# ========================

class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='logbook_student_profile'  # Changed related_name to avoid conflicts
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
        related_name='supervised_students'  # Assuming this is already unique
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Auto-create profile for new student users
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    if created and getattr(instance, 'role', None) == 'student':
        StudentProfile.objects.create(
            user=instance,
            year_of_study=1,
            registration_number=f"TEMP{instance.pk}",
            course="Unknown"
        )
        
##############################

##log entry

#############################

class LogEntry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='log_entries'
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='log_entries'
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='log_entries'
    )
    date = models.DateField()
    day_number = models.PositiveIntegerField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    description = models.TextField()
    trainee_signature = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    approved = models.BooleanField(default=False)  # legacy field for compatibility
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_log_entries'
    )
    approved_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

# ========================
# Uploaded Files
# ========================

class UploadedFile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_files'
    )
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name.split('/')[-1]}"


# ========================
# Weekly Progress Report
# ========================

class ProgressReport(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress_reports'
    )
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_reports'
    )
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
# Task Management
# ========================

class Task(models.Model):
    description = models.TextField()
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='logbook_tasks_assigned'  # Changed related_name to avoid conflict with users.AssignedTask
    )
    assigned_to = models.ManyToManyField(StudentProfile, related_name='tasks_received')
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Task by {self.assigned_by.username} on {self.assigned_at.strftime('%Y-%m-%d')}"


# ========================
# Assigned Task (Deprecated or Alternative)
# ========================

class AssignedTask(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assigned_tasks',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title
