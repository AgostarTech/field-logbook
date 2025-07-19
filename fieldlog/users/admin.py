from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, SupervisorProfile, StudentProfile, LogEntry, AssignedTask, SupervisorUpload


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'department', 'profile_picture')}),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'phone')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'registration_number', 'course', 'year_of_study')
    search_fields = ('user__username', 'registration_number', 'course')


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('student__user__username',)


@admin.register(AssignedTask)
class AssignedTaskAdmin(admin.ModelAdmin):
    list_display = ('task_title', 'supervisor', 'student', 'due_date', 'status', 'is_completed')
    list_filter = ('status', 'is_completed', 'due_date')
    search_fields = ('task_title', 'supervisor__username', 'student__user__username')


@admin.register(SupervisorUpload)
class SupervisorUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'uploaded_by__username')
