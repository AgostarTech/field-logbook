from django.contrib import admin
from .models import LogEntry

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'description', 'approved']  # Replace 'activity' with 'description' or another existing field

admin.site.register(LogEntry, LogEntryAdmin)
