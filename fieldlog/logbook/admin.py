from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from .models import LogEntry

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'description', 'approved']  # Ensure all these fields exist

# Unregister first (safe even if not registered)
try:
    admin.site.unregister(LogEntry)
except admin.sites.NotRegistered:
    pass

# Now register
admin.site.register(LogEntry, LogEntryAdmin)
