from datetime import datetime, timedelta
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.db import IntegrityError

from .models import (
    LogEntry,
    UploadedFile,
    Place,
    Institution,
    ProgressReport,
    StudentProfile,
    Task,
)
from .forms import (
    CustomUserUpdateForm,
    StudentProfileUpdateForm,
    LogEntryForm,
    FileUploadForm,
    ProgressReportForm,
    StudentSignUpForm,
    TaskAssignForm,
)

User = get_user_model()

# ---------- Profile Views ----------

@login_required
def profile_view(request):
    profile = getattr(request.user, 'student_profile', None)
    return render(request, 'logbook/profile.html', {'user': request.user, 'profile': profile})

@login_required
def profile_update(request):
    profile = getattr(request.user, 'student_profile', None)
    if not profile:
        # Redirect or create profile logic here
        return redirect('logbook:profile')

    if request.method == 'POST':
        profile_form = StudentProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('logbook:profile')
    else:
        profile_form = StudentProfileUpdateForm(instance=profile)

    return render(request, 'logbook/profile_update.html', {'profile_form': profile_form})

# ---------- Utility Function ----------

def working_days_since(start_date, current_date):
    day_count = 0
    current = start_date
    while current <= current_date:
        if current.weekday() < 5:  # Monday to Friday
            day_count += 1
        current += timedelta(days=1)
    return day_count

# ---------- Log Entry Views ----------

@login_required
def new_logentry(request):
    profile = getattr(request.user, 'student_profile', None)
    if not profile or not profile.field_start_date:
        messages.error(request, "Please update your profile with field start date before adding log entries.")
        return redirect('logbook:profile_update')

    if request.method == 'POST':
        form = LogEntryForm(request.POST)
        if form.is_valid():
            logentry = form.save(commit=False)
            logentry.user = request.user
            logentry.day_number = working_days_since(profile.field_start_date, logentry.date)
            logentry.save()
            messages.success(request, "New log entry created.")
            return redirect('logbook:view_last_entry')
    else:
        form = LogEntryForm(initial={
            'date': now().date(),
            'start_time': now().time().replace(microsecond=0),
        })

    return render(request, 'logbook/new.html', {
        'form': form,
        'places': Place.objects.all(),
        'institutions': Institution.objects.none(),
        'entry_count': LogEntry.objects.filter(user=request.user).count(),
        'field_start_date': profile.field_start_date.strftime('%Y-%m-%d'),
        'max_days': 25,
    })

@login_required
def view_last_entry(request):
    entry = LogEntry.objects.filter(user=request.user).order_by('-date').first()
    return render(request, 'logbook/view_last_entry.html', {'entry': entry})

@login_required
def update_entry(request):
    entry = LogEntry.objects.filter(user=request.user).order_by('-date').first()
    if not entry:
        messages.warning(request, "No log entry found to update.")
        return redirect('logbook:new_logentry')

    if request.method == 'POST':
        form = LogEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Log entry updated successfully.")
            return redirect('logbook:view_last_entry')
    else:
        form = LogEntryForm(instance=entry)

    return render(request, 'logbook/update_entry.html', {'form': form})

@login_required
def view_logs(request):
    logs = LogEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'logbook/view_logs.html', {'logs': logs})

@login_required
def get_institutions(request):
    place_id = request.GET.get('place_id')
    institutions = Institution.objects.filter(place_id=place_id).values('id', 'name')
    return JsonResponse(list(institutions), safe=False)

# ---------- Progress Report Views ----------

@login_required
def progress_report_view(request):
    user = request.user
    profile = getattr(user, 'student_profile', None)
    trainee_name = f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username
    organization_name = profile.organization_name if profile else "N/A"
    registration_number = profile.registration_number if profile else "N/A"

    start_date = datetime(2025, 6, 1)  # Adjust this as needed

    weeks = [
        (1, 'supervisor_comment_week_1', start_date, start_date + timedelta(days=6)),
        (2, 'supervisor_comment_week_2', start_date + timedelta(days=7), start_date + timedelta(days=13)),
        (3, 'supervisor_comment_week_3', start_date + timedelta(days=14), start_date + timedelta(days=20)),
        (4, 'supervisor_comment_week_4', start_date + timedelta(days=21), start_date + timedelta(days=27)),
        (5, 'supervisor_comment_week_5', start_date + timedelta(days=28), start_date + timedelta(days=34)),
    ]

    if request.method == 'POST':
        form = ProgressReportForm(request.POST)
        if form.is_valid():
            lat = form.cleaned_data.get('latitude')
            lon = form.cleaned_data.get('longitude')

            for week_number, field_name, _, _ in weeks:
                comment = form.cleaned_data.get(field_name)
                if comment:
                    ProgressReport.objects.update_or_create(
                        student=user,
                        week_number=week_number,
                        defaults={'supervisor_comment': comment, 'latitude': lat, 'longitude': lon}
                    )
            messages.success(request, "Progress report saved.")
            return redirect('users:dashboard')
    else:
        initial_data = {}
        for week_number, field_name, _, _ in weeks:
            try:
                pr = ProgressReport.objects.get(student=user, week_number=week_number)
                initial_data[field_name] = pr.supervisor_comment
                initial_data['latitude'] = pr.latitude
                initial_data['longitude'] = pr.longitude
            except ProgressReport.DoesNotExist:
                initial_data[field_name] = ''
        form = ProgressReportForm(initial=initial_data)

    detailed_weeks = []
    for week_number, comment_field, start, end in weeks:
        try:
            pr = ProgressReport.objects.get(student=user, week_number=week_number)
            supervisor_comment = pr.supervisor_comment
            latitude = pr.latitude
            longitude = pr.longitude
        except ProgressReport.DoesNotExist:
            supervisor_comment = ''
            latitude = None
            longitude = None

        detailed_weeks.append({
            'week_number': week_number,
            'start_date': start.strftime('%Y-%m-%d'),
            'end_date': end.strftime('%Y-%m-%d'),
            'supervisor_comment': supervisor_comment,
            'latitude': latitude,
            'longitude': longitude,
            'form_field': form[comment_field],
        })

    return render(request, 'logbook/progress_report.html', {
        'form': form,
        'detailed_weeks': detailed_weeks,
        'trainee_name': trainee_name,
        'organization_name': organization_name,
        'registration_number': registration_number,
    })

# ---------- File Views ----------

@login_required
def view_files(request):
    files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
    for f in files:
        f.is_image = f.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
    return render(request, 'logbook/view_files.html', {'files': files})

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            upload.save()
            messages.success(request, "File uploaded successfully.")
            return redirect('logbook:view_files')
        messages.error(request, "Please fix the errors.")
    else:
        form = FileUploadForm()
    return render(request, 'logbook/upload_file.html', {'form': form})

@login_required
def download_files(request):
    files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
    for f in files:
        f.is_image = f.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
    return render(request, 'logbook/download_files.html', {'files': files})

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    if request.method == 'POST':
        file.delete()
        messages.success(request, "File deleted successfully.")
    return redirect('logbook:download_files')

# ---------- Signup View ----------

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST, request.FILES or None)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, "Account created and logged in.")
                return redirect('logbook:profile')
            except IntegrityError:
                form.add_error('registration_number', "This registration number already exists. Please choose another.")
        else:
            messages.error(request, "Please correct the errors in the signup form.")
    else:
        form = StudentSignUpForm()

    return render(request, 'users/student_signup.html', {'form': form})

# ---------- Task Assignment ----------

@login_required
def assign_task(request):
    if request.method == 'POST':
        form = TaskAssignForm(request.POST, user=request.user)
        if form.is_valid():
            task_description = form.cleaned_data['task_description']
            student_ids = form.cleaned_data['student_ids']

            task = Task.objects.create(
                assigned_by=request.user,
                description=task_description,
            )
            for student_profile in student_ids:
                task.assigned_to.add(student_profile)

            messages.success(request, "Task assigned successfully.")
            return redirect('logbook:dashboard')
        messages.error(request, "Please correct errors in the task form.")
    else:
        form = TaskAssignForm(user=request.user)

    assigned_students = StudentProfile.objects.filter(supervisor=request.user)
    return render(request, 'logbook/assign_task.html', {
        'form': form,
        'assigned_students': assigned_students,
    })

# ---------- Dashboard ----------

@login_required
def dashboard(request):
    user = request.user
    role = getattr(user, 'role', None)

    if role == 'student':
        return render(request, 'users/student_dashboard.html')

    elif role in ['onstation', 'oncampus']:
        # Get all students assigned to this supervisor
        assigned_students = User.objects.filter(role='student', student_profile__supervisor=user).distinct()
        total_students = User.objects.filter(role='student')

        # Filter logs where user in assigned_students
        logs = LogEntry.objects.filter(user__in=assigned_students)

        student_progress = []
        for student in assigned_students:
            total_logs = logs.filter(user=student).count()
            approved_logs = logs.filter(user=student, status='approved').count()  # adjust if status is boolean
            progress_percent = (approved_logs / total_logs * 100) if total_logs else 0

            student_progress.append({
                'student': student,
                'total_logs': total_logs,
                'approved_logs': approved_logs,
                'progress_percent': round(progress_percent, 2),
            })

        pending_logs = logs.filter(status='pending')
        approved_logs = logs.filter(status='approved')

        assigned_tasks = Task.objects.filter(assigned_by=user)

        context = {
            'assigned_students': assigned_students,
            'student_progress': student_progress,
            'total_students': total_students,
            'total_students_count': total_students.count(),
            'assigned_students_count': assigned_students.count(),
            'pending_logs': pending_logs,
            'approved_logs': approved_logs,
            'pending_logs_count': pending_logs.count(),
            'approved_logs_count': approved_logs.count(),
            'assigned_tasks': assigned_tasks,
        }
        return render(request, 'users/supervisor_dashboard.html', context)

    return render(request, 'users/dashboard.html')

# ---------- Create & Edit Log Entries ----------

@login_required
def create_entry(request):
    if request.method == 'POST':
        form = LogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, "Log entry created successfully.")
            return redirect('logbook:view_last_entry')
    else:
        form = LogEntryForm()
    return render(request, 'logbook/create_log_entry.html', {'form': form})

@login_required
def edit_entry(request, pk):
    entry = get_object_or_404(LogEntry, pk=pk)

    if request.method == 'POST':
        form = LogEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Log entry updated successfully.")
            return redirect('logbook:student_dashboard')
    else:
        form = LogEntryForm(instance=entry)

    return render(request, 'logbook/edit_entry.html', {'form': form})

@login_required
def log_detail(request, pk):
    entry = get_object_or_404(LogEntry, pk=pk)
    return render(request, 'logbook/log_detail.html', {'entry': entry})

# ---------- Task Completion ----------

@login_required
def mark_task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, assigned_by=request.user)
    task.completed = True
    task.save()
    messages.success(request, "Task marked as complete.")
    return redirect('logbook:dashboard')

# ---------- Placeholder ----------

@login_required
def evaluation_forms_view(request):
    return render(request, 'logbook/evaluation_forms.html')

# ---------- Student Dashboard ----------

@login_required
def student_dashboard(request):
    context = {}
    return render(request, 'logbook/student_dashboard.html', context)

# ---------- Add Entry Views (simplified placeholders) ----------

@login_required
def add_entry(request):
    if request.method == 'POST':
        # handle form submission logic here
        pass
    return render(request, 'logbook/add_entry.html')

@login_required
def add_entry_view(request):
    return render(request, 'logbook/add_entry.html')
