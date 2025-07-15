
# Register your models here.
from django.contrib import admin
from .models import LogEntry, StudentProfile

admin.site.register(LogEntry)
admin.site.register(StudentProfile)
