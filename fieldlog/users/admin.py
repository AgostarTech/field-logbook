from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import (
    CustomUser,
    Department,
    StudentProfile,
    AssignedTask,
    SupervisorUpload,
    OnStationSupervisor,
    OnCampusSupervisor,
)
from logbook.models import LogEntry


# =============== Custom Inlines ===============
class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'


# =============== Custom User Admin ===============
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    inlines = [StudentProfileInline]

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'department', 'profile_picture')
        }),
    )


# =============== Department Admin ===============
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# =============== On-Campus Supervisor Admin ===============
@admin.register(OnCampusSupervisor)
class OnCampusSupervisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_approved')
    list_filter = ('is_approved', 'department')
    search_fields = ('user__username', 'user__email')

    actions = ['approve_selected']

    @admin.action(description="Mark selected supervisors as approved")
    def approve_selected(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} supervisor(s) marked as approved.")


# =============== On-Station Supervisor Admin ===============
@admin.register(OnStationSupervisor)
class OnStationSupervisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'position')
    search_fields = ('user__username', 'company_name')


# =============== Student Profile Admin ===============
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'registration_number', 'course', 'year_of_study')
    search_fields = ('user__username', 'registration_number', 'course')


# =============== Log Entry Admin ===============
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'approved_by', 'approved_at')
    list_filter = ('status', 'date')
    search_fields = ('student__user__username',)

    actions = ['approve_logs', 'reject_logs']

    @admin.action(description="Approve selected logs")
    def approve_logs(self, request, queryset):
        updated_count = 0
        for log in queryset:
            if log.status != 'approved':
                log.status = 'approved'
                log.approved_by = request.user
                log.approved_at = timezone.now()
                log.save()
                updated_count += 1
        self.message_user(request, f"{updated_count} log(s) approved.")

    @admin.action(description="Reject selected logs")
    def reject_logs(self, request, queryset):
        updated_count = 0
        for log in queryset:
            if log.status != 'rejected':
                log.status = 'rejected'
                log.approved_by = request.user
                log.approved_at = timezone.now()
                log.save()
                updated_count += 1
        self.message_user(request, f"{updated_count} log(s) rejected.")


# =============== Assigned Task Admin ===============
@admin.register(AssignedTask)
class AssignedTaskAdmin(admin.ModelAdmin):
    list_display = ('task_title', 'supervisor', 'student', 'due_date', 'status', 'is_completed')
    list_filter = ('status', 'is_completed', 'due_date')
    search_fields = ('task_title', 'supervisor__username', 'student__user__username')


# =============== Supervisor Upload Admin ===============
@admin.register(SupervisorUpload)
class SupervisorUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'uploaded_by__username')
