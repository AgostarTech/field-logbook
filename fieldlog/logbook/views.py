from datetime import datetime, timedelta
from django.utils.timezone import now
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import login

from .models import (
    LogEntry,
    UploadedFile,
    Place,
    Institution,
    ProgressReport,
    StudentProfile,
)
from .forms import (
    CustomUserUpdateForm,
    StudentProfileUpdateForm,
    LogEntryForm,
    FileUploadForm,
    ProgressReportForm,
    StudentSignUpForm,  # make sure this is imported
)


# ==========================
# Profile Views
# ==========================

@login_required
def profile_view(request):
    """Display user profile."""
    context = {
        'user': request.user,
        'profile': getattr(request.user, 'student_profile', None),
    }
    return render(request, 'logbook/profile.html', context)

@login_required
def profile_update(request):
    """Update user and student profile."""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = StudentProfile(user=request.user)

    if request.method == 'POST':
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        profile_form = StudentProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('logbook:profile')

    else:
        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = StudentProfileUpdateForm(instance=profile)

    return render(request, 'logbook/profile_update.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


# ==========================
# Logbook Entry Views
# ==========================

@login_required
def log_activity_view(request):
    """View main log activity page."""
    return render(request, 'logbook/log_activity.html')


@login_required
def create_entry(request):
    """Create a new log entry."""
    if request.method == 'POST':
        form = LogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('logbook:view_last_entry')
    else:
        form = LogEntryForm()
    return render(request, 'logbook/create_log_entry.html', {'form': form})


@login_required
def view_last_entry(request):
    """View the most recent log entry of the user."""
    entry = LogEntry.objects.filter(user=request.user).order_by('-date').first()
    return render(request, 'logbook/view_last_entry.html', {'entry': entry})


@login_required
def update_entry(request):
    """Update the most recent log entry."""
    entry = LogEntry.objects.filter(user=request.user).order_by('-date').first()
    if not entry:
        return redirect('logbook:create_entry')

    if request.method == 'POST':
        form = LogEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('logbook:view_last_entry')
    else:
        form = LogEntryForm(instance=entry)
    return render(request, 'logbook/update_entry.html', {'form': form})


# ==========================
# Helper Function: Working Days Calculator (Exclude weekends)
# ==========================

def working_days_since(start_date, current_date):
    """Calculate working days (Mon-Fri) between two dates, inclusive."""
    day_count = 0
    current = start_date
    while current <= current_date:
        if current.weekday() < 5:  # Monday=0 ... Friday=4
            day_count += 1
        current += timedelta(days=1)
    return day_count


# ==========================
# New Log Entry with Automatic Day Number Calculation
# ==========================

@login_required
def new_logentry(request):
    """Create a new log entry with automatic day counting excluding weekends."""
    user = request.user
    profile = getattr(user, 'student_profile', None)

    # Redirect if no start date set in profile
    if not profile or not getattr(profile, 'field_start_date', None):
        return redirect('logbook:profile_update')

    field_start_date = profile.field_start_date

    if request.method == 'POST':
        form = LogEntryForm(request.POST)
        if form.is_valid():
            logentry = form.save(commit=False)
            logentry.user = user
            logentry.day_number = working_days_since(field_start_date, logentry.date)
            logentry.save()
            return redirect('logbook:view_last_entry')
    else:
        form = LogEntryForm(initial={
            'date': now().date(),
            'start_time': now().time().replace(microsecond=0),
        })

    return render(request, 'logbook/new.html', {
        'form': form,
        'places': Place.objects.all(),
        'institutions': Institution.objects.none(),  # AJAX will load based on place
        'entry_count': LogEntry.objects.filter(user=user).count(),
        'field_start_date': field_start_date.strftime('%Y-%m-%d'),
        'max_days': 25,  # max expected working days
    })


# ==========================
# AJAX Views
# ==========================

@login_required
def get_institutions(request):
    """Return institutions filtered by place (AJAX)."""
    place_id = request.GET.get('place_id')
    institutions = Institution.objects.filter(place_id=place_id).values('id', 'name')
    return JsonResponse(list(institutions), safe=False)


# ==========================
# Progress & Evaluation Views
# ==========================

@login_required
def evaluation_forms_view(request):
    """Show evaluation forms page."""
    return render(request, 'logbook/evaluation_forms.html')


@login_required
def progress_report_view(request):
    user = request.user

    # Get trainee profile
    try:
        profile = StudentProfile.objects.get(user=user)
        trainee_name = f"{user.first_name} {user.last_name}"
        organization_name = getattr(profile, 'organization_name', 'N/A')
        registration_number = profile.registration_number
    except StudentProfile.DoesNotExist:
        trainee_name = "N/A"
        organization_name = "N/A"
        registration_number = "N/A"

    start_date = datetime(2025, 6, 1)  # FTP start date (adjust as needed)

    # Weeks info
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
                        defaults={
                            'supervisor_comment': comment,
                            'latitude': lat,
                            'longitude': lon,
                        }
                    )
            return redirect('dashboard')
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

    # Build detailed week reports list for template
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

    context = {
        'form': form,
        'detailed_weeks': detailed_weeks,
        'trainee_name': trainee_name,
        'organization_name': organization_name,
        'registration_number': registration_number,
    }

    return render(request, 'logbook/progress_report.html', context)


# ==========================
# File Operations Views
# ==========================

@login_required
def view_files(request):
    """View uploaded files with image detection."""
    files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
    for f in files:
        f.is_image = f.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
    return render(request, 'logbook/view_files.html', {'files': files})


@login_required
def upload_file(request):
    """Upload a new file."""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.user = request.user
            uploaded_file.save()
            return redirect('logbook:view_files')
    else:
        form = FileUploadForm()
    return render(request, 'logbook/upload_file.html', {'form': form})


@login_required
def download_files(request):
    """View files for download."""
    files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
    for f in files:
        f.is_image = f.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
    return render(request, 'logbook/download_files.html', {'files': files})


@login_required
def delete_file(request, file_id):
    """Delete a file owned by the user."""
    file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    if request.method == 'POST':
        file.delete()
    return redirect('logbook:download_files')


# ==========================
# Student Signup View
# ==========================

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST, request.FILES or None)
        if form.is_valid():
            user = form.save()  # saves User

            # Create StudentProfile WITHOUT year_of_study
            StudentProfile.objects.create(
                user=user,
                academic_year=form.cleaned_data.get('academic_year'),
                registration_number=form.cleaned_data.get('registration_number'),
                profile_picture=form.cleaned_data.get('profile_picture'),
                phone_number=form.cleaned_data.get('phone_number'),
                field_start_date=form.cleaned_data.get('field_start_date'),
                organization_name=form.cleaned_data.get('organization_name'),
            )

            login(request, user)
            return redirect('logbook:profile')
    else:
        form = StudentSignUpForm()

    return render(request, 'users/student_signup.html', {'form': form})
