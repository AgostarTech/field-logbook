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

#===========================================




# logbook/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from logbook.models import (
    LogEntry,
    ProgressReport,
    EvaluationForm,
    UploadedFile,
    Task,
    AssignedTask,
    StudentProfile
)

User = get_user_model()

@login_required
def get_log_profile_data(request, user_id=None):
    # Use the provided user_id or fallback to the logged-in user
    target_user = User.objects.get(pk=user_id) if user_id else request.user

    student_profile = getattr(target_user, 'logbook_student_profile', None)

    log_entries = LogEntry.objects.filter(user=target_user).values()
    progress_reports = ProgressReport.objects.filter(student=target_user).values()
    evaluations = EvaluationForm.objects.filter(student=target_user).values()
    uploads = UploadedFile.objects.filter(user=target_user).values()
    assigned_tasks = AssignedTask.objects.filter(student=target_user).values()

    # Get tasks only if the user has a student profile
    tasks = []
    if student_profile:
        tasks = Task.objects.filter(assigned_to=student_profile).values()

    # Combine everything into one dict
    log_data = {
        "user_id": target_user.id,
        "username": target_user.username,
        "log_entries": list(log_entries),
        "progress_reports": list(progress_reports),
        "evaluations": list(evaluations),
        "uploaded_files": list(uploads),
        "tasks": list(tasks),
        "assigned_tasks": list(assigned_tasks),
    }

    return JsonResponse(log_data, safe=False)



#==============================================

# ---------- Profile Views ----------

############################################





@login_required
def profile_view(request):
    profile = getattr(request.user, 'student_profile', None)
    return render(request, 'logbook/profile.html', {'user': request.user, 'profile': profile})



#####################################################













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


#+++++++++++++++++++++++++++++++++++++++++++


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.timezone import now
from .forms import LogEntryForm
from .models import LogEntry
from .utils import working_days_since  # Adjust if you use this from another module

@login_required
def new_logentry(request):
    profile = getattr(request.user, 'studentprofile', None)
    
    if not profile or not profile.field_start_date:
        messages.error(request, "Please update your profile with field start date before adding log entries.")
        return redirect('logbook:profile_update')

    if request.method == 'POST':
        form = LogEntryForm(request.POST)
        if form.is_valid():
            logentry = form.save(commit=False)
            logentry.user = request.user
            logentry.day_number = working_days_since(profile.field_start_date, logentry.date)

            # Set company/place/institution from student profile (load automatically)
            logentry.company_place_institution = profile.company_place_institution
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
        'entry_count': LogEntry.objects.filter(user=request.user).count(),
        'field_start_date': profile.field_start_date.strftime('%Y-%m-%d'),
        'company_place': profile.company_place_institution,  # Pass to template for display only
        'max_days': 25,
    })



###++++++++++++++++++++++++++++++++++++++++++++++++++




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from logbook.models import LogEntry

@login_required
def view_last_entry(request):
    # Last 2 entries (or recent few)
    entries = LogEntry.objects.filter(user=request.user).order_by('-created_at')[:2]

    # All entries
    all_entries = LogEntry.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'logbook/view_last_entry.html', {
        'entries': entries,
        'all_entries': all_entries,
    })


#####################################

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
def view_logs(request, student_id):
    user = request.user

    if user.role == 'student':
        # Students see only their own logs
        logs = LogEntry.objects.filter(user=user).order_by('-created_at')

    elif user.role in ['station_supervisor', 'university_supervisor']:
        # Supervisors see logs of all students they supervise
        logs = LogEntry.objects.filter(user__role='student').order_by('-created_at')

    elif user.role == 'admin':
        # Admins can view everything
        logs = LogEntry.objects.all().order_by('-created_at')

    else:
        # Default fallback (optional)
        logs = LogEntry.objects.none()

    return render(request, 'logbook/view_logs.html', {'logs': logs})

@login_required
def get_institutions(request):
    place_id = request.GET.get('place_id')
    institutions = Institution.objects.filter(place_id=place_id).values('id', 'name')
    return JsonResponse(list(institutions), safe=False)
###############################



###task progress



#########################################

from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ProgressReport
from .forms import ProgressReportForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta

@login_required
def progress_report_view(request):
    user = request.user
    profile = getattr(user, 'student_profile', None)
    is_student = hasattr(user, 'student_profile')

    trainee_name = f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username

    if profile:
        organization_name = profile.organization.name if hasattr(profile, 'organization') and profile.organization else "N/A"
        registration_number = getattr(profile, 'registration_number', "N/A")
    else:
        organization_name = "N/A"
        registration_number = "N/A"

    start_date = datetime(2025, 6, 1)
    weeks = [
        (1, 'supervisor_comment_week_1', start_date, start_date + timedelta(days=6)),
        (2, 'supervisor_comment_week_2', start_date + timedelta(days=7), start_date + timedelta(days=13)),
        (3, 'supervisor_comment_week_3', start_date + timedelta(days=14), start_date + timedelta(days=20)),
        (4, 'supervisor_comment_week_4', start_date + timedelta(days=21), start_date + timedelta(days=27)),
        (5, 'supervisor_comment_week_5', start_date + timedelta(days=28), start_date + timedelta(days=34)),
    ]

    if request.method == 'POST' and not is_student:
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
        form = ProgressReportForm(initial=initial_data) if not is_student else None

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

        if form:
            editable_html = form[comment_field].as_widget()
            readonly_html = form[comment_field].as_widget(attrs={'readonly': 'readonly', 'disabled': 'disabled'})
        else:
            editable_html = None
            readonly_html = None

        detailed_weeks.append({
            'week_number': week_number,
            'start_date': start.strftime('%Y-%m-%d'),
            'end_date': end.strftime('%Y-%m-%d'),
            'supervisor_comment': supervisor_comment,
            'latitude': latitude,
            'longitude': longitude,
            'form_field_html': editable_html,
            'form_field_html_readonly': readonly_html,
        })

    return render(request, 'logbook/progress_report.html', {
        'form': form,
        'detailed_weeks': detailed_weeks,
        'trainee_name': trainee_name,
        'organization_name': organization_name,
        'registration_number': registration_number,
        'is_student': is_student,
    })

# ---------- File Views ----------



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from logbook.models import UploadedFile
from users.models import StudentProfile, SupervisorProfile

@login_required
def view_files(request):
    files = UploadedFile.objects.all().order_by('-uploaded_at')

    for f in files:
        f.is_image = f.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
        user = f.user
        f.uploader_name = f"{user.first_name} {user.last_name}"
        f.phone_number = getattr(user, 'phone_number', 'N/A')

        if user.role == 'student':
            if hasattr(user, 'studentprofile'):
                f.registration_number = user.studentprofile.registration_number
            else:
                f.registration_number = 'N/A'
            f.role_position = ''
        else:
            f.registration_number = ''
            if hasattr(user, 'supervisorprofile'):
                sp = user.supervisorprofile
                f.role_position = f"{user.role.replace('_', ' ').title()} - {sp.position}"
            else:
                f.role_position = user.role.title()

    return render(request, 'logbook/view_files.html', {'files': files})




# logbook/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from logbook.forms import FileUploadForm  # Ensure your form includes 'description'
from logbook.models import UploadedFile

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
        else:
            messages.error(request, "Please fix the errors.")
    else:
        form = FileUploadForm()
    
    return render(request, 'logbook/upload_file.html', {'form': form})



#=======================================================



#======================================




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from logbook.models import UploadedFile
from users.models import StudentProfile, SupervisorProfile

@login_required
def download_files(request):
    files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')

    for f in files:
        f.is_image = f.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
        user = f.user
        f.uploader_name = f"{user.first_name} {user.last_name}"
        f.upload_time = f.uploaded_at
        f.file_id = f.id
        f.file_type = 'Image' if f.is_image else 'Document'
        f.description = getattr(f, 'description', '') or '-'

        if user.role == 'student':
            if hasattr(user, 'studentprofile'):
                f.registration_number = user.studentprofile.registration_number
            else:
                f.registration_number = 'N/A'
            f.role_position = ''
        else:
            f.registration_number = ''
            if hasattr(user, 'supervisorprofile'):
                sp = user.supervisorprofile
                f.role_position = f"{user.role.replace('_', ' ').title()} - {sp.position}"
            else:
                f.role_position = user.role.title()

    return render(request, 'logbook/download_files.html', {'files': files})

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id, user=request.user)
    if request.method == 'POST':
        file.delete()
        messages.success(request, "File deleted successfully.")
    return redirect('logbook:download_files')





#==============================

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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import EvaluationForm
from django.contrib import messages

@login_required
def evaluation_forms_view(request):
    user = request.user

    try:
        form_instance = EvaluationForm.objects.get(student=user)
    except EvaluationForm.DoesNotExist:
        form_instance = None

    if request.method == 'POST':
        if form_instance and form_instance.submitted:
            messages.warning(request, "You have already submitted your evaluation.")
            return redirect('evaluation_forms')  # prevent resubmission

        data = {
            'strengths': request.POST.get('strengths'),
            'benefits_personal': request.POST.get('benefits_personal'),
            'org_benefits': request.POST.get('org_benefits'),
            'community_benefits': request.POST.get('community_benefits'),
            'relevance': request.POST.get('relevance'),
            'constraint': request.POST.get('constraint'),
            'solution': request.POST.get('solution'),
            'suggestions': request.POST.get('suggestions'),
            'knowledge': request.POST.get('knowledge'),
            'skills': request.POST.get('skills'),
            'supervision': request.POST.get('supervision'),
            'evaluation_method': request.POST.get('evaluation_method'),
            'submitted': True,
        }

        if form_instance:
            for key, value in data.items():
                setattr(form_instance, key, value)
            form_instance.save()
        else:
            EvaluationForm.objects.create(student=user, **data)

        messages.success(request, "Evaluation submitted successfully.")
        return redirect('evaluation_forms')

    context = {
        'form_data': form_instance,
        'is_submitted': form_instance.submitted if form_instance else False,
    }

    return render(request, 'logbook/evaluation_forms.html', context)

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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LogEntry

@login_required
def all_students_logs(request):
    user_role = getattr(request.user, 'role', None)
    is_supervisor = request.user.is_staff or user_role not in ['oncampus', 'onstation']

    if is_supervisor:
        logs = LogEntry.objects.select_related('user').order_by('-date', '-created_at')
    elif user_role in ['oncampus', 'onstation']:
        logs = LogEntry.objects.filter(user=request.user).order_by('-date', '-created_at')
    else:
        messages.error(request, "You do not have permission to view logs.")
        return redirect('logbook:dashboard')

    return render(request, 'logbook/all_students_logs.html', {
        'logs': logs,
        'is_supervisor': is_supervisor
    })


#================================================





from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import CustomUser
from logbook.models import LogEntry

@login_required
def student_logs(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role='student')
    logs = LogEntry.objects.filter(user=student).select_related('approved_by').order_by('-created_at')
    return render(request, 'logbook/student_logs.html', {
        'student': student,
        'logs': logs,
    })









#=========================================

import io
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import qrcode
from .models import LogEntry

@login_required
def download_entry_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    user = request.user

    # Starting Y position
    y = height - 80

    # Draw user profile picture if available
    if hasattr(user, 'profile_picture') and user.profile_picture:
        try:
            img_path = user.profile_picture.path  # local file path
            p.drawImage(ImageReader(img_path), 50, y - 70, width=60, height=60)
        except Exception:
            pass

    # Draw user info text next to profile pic
    text_x = 120
    p.setFont("Helvetica-Bold", 14)
    p.drawString(text_x, y, f"{user.first_name} {user.last_name}")
    p.setFont("Helvetica", 12)
    y -= 20
    p.drawString(text_x, y, f"Registration No: {getattr(user, 'registration_number', 'N/A')}")
    y -= 20
    p.drawString(text_x, y, f"Username: {user.username}")

    y -= 50

    # Draw title
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "Logbook Entries")
    y -= 30

    # Fetch user log entries
    entries = LogEntry.objects.filter(user=user).order_by('created_at')

    p.setFont("Helvetica", 11)

    # Draw each entry - customize as needed
    for entry in entries:
        entry_date = entry.created_at.strftime("%Y-%m-%d")
        place = getattr(entry, 'place', '')
        description = (entry.description[:100] + '...') if len(entry.description) > 100 else entry.description

        entry_text = f"{entry_date} | {place} | {description}"
        p.drawString(50, y, entry_text)
        y -= 20

        if y < 150:
            p.showPage()
            y = height - 80
            p.setFont("Helvetica", 11)

    # Leave space for signature line
    y -= 50
    p.line(50, y, 250, y)  # signature line
    y -= 15
    p.drawString(50, y, "Signature")

    # Generate QR code (for example, encode user's profile url or id)
    qr_data = f"https://yourdomain.com/user/{user.pk}/logbook"  # customize your URL
    qr = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)
    qr_img = ImageReader(qr_buffer)

    # Place QR code bottom-right
    qr_size = 100
    p.drawImage(qr_img, width - qr_size - 50, 50, width=qr_size, height=qr_size)

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"{user.username}_log_entries.pdf")


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import LogEntry

@login_required
def all_students_logs(request):
    user = request.user

    if user.is_staff or getattr(user, 'role', None) in ['onstation', 'oncampus']:
        logs = LogEntry.objects.select_related('user', 'institution', 'place').order_by('-date', '-created_at')

    elif hasattr(user, 'student_profile'):
        # Show only logs for the logged-in student
        logs = LogEntry.objects.filter(user=user).select_related('user', 'institution', 'place').order_by('-date', '-created_at')

    else:
        # For supervisors: show logs of students they supervise
        supervised_students = user.supervised_students.all()  # adjust related_name if needed
        student_users = [s.user for s in supervised_students]
        logs = LogEntry.objects.filter(user__in=student_users).select_related('user', 'institution', 'place').order_by('-date', '-created_at')

    return render(request, 'logbook/all_students_logs.html', {'logs': logs})



from django.http import HttpResponse

def download_log(request, pk):
    return HttpResponse("Download log not implemented yet.")

def update_log(request, pk):
    return HttpResponse("Update log not implemented yet.")

def log_comments(request, pk):
    return HttpResponse("Log comments not implemented yet.")

def delete_log(request, pk):
    return HttpResponse("Delete log not implemented yet.")


