from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date



User = get_user_model()

# ========================
# Location and Institution
# ========================

class Place(models.Model):
    """Represents a physical location or region."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Institution(models.Model):
    """Represents an organization where students are placed."""
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='institutions')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.place.name})"


# ========================
# Student Profile
# ========================

class StudentProfile(models.Model):
    """Extended profile for a student user."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    registration_number = models.CharField(max_length=30, unique=True)
    year_of_study = models.PositiveSmallIntegerField()
    academic_year = models.CharField(max_length=20)
    field_start_date = models.DateField(null=True, blank=True, default=date.today)
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """Automatically create a StudentProfile when a new User is created."""
    if created:
        StudentProfile.objects.create(user=instance)


# ========================
# Logbook Entry
# ========================

class LogEntry(models.Model):
    """Daily log entry written by the student during fieldwork."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='log_entries')
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True, related_name='log_entries')
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True, related_name='log_entries')
    date = models.DateField()
    day_number = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Sequential day number from internship start, excluding weekends"
    )
    start_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    description = models.TextField(help_text="Daily description of tasks or assignments.")
    trainee_signature = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    approved = models.BooleanField(default=False, help_text="Approved by supervisor")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.institution or 'No Institution'})"


# ========================
# Uploaded Files
# ========================

class UploadedFile(models.Model):
    """File uploads related to fieldwork (reports, images, documents)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"


# ========================
# Weekly Progress Report
# ========================

class ProgressReport(models.Model):
    """Weekly progress summary submitted by a student."""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_reports')
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_reports')
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
        return f"Progress Report Week {self.week_number} for {self.student.username}"
