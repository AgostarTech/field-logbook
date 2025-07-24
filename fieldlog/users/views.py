from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.template.loader import get_template
from xhtml2pdf import pisa
from logbook.models import LogEntry


from .forms import (
    StudentSignUpForm,
    OnStationSupervisorSignUpForm,
    OnCampusSupervisorSignUpForm,
    ProfileForm,
    SupervisorUploadForm,
)
from .models import (
    CustomUser,
    AssignedTask,
    StudentProfile,
    SupervisorUpload,
    OnStationSupervisor,
    OnCampusSupervisor,
)
from logbook.models import LogEntry
from logbook.forms import StudentProfileForm

User = get_user_model()


# ===== Basic Views =====

def home(request):
    return render(request, 'users/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('/admin/')
            return redirect('users:dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')


def signup_select(request):
    return render(request, 'users/signup_select.html')


# ===== Signup Views =====

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:dashboard')
        messages.error(request, "Please fix the errors below.")
    else:
        form = StudentSignUpForm()
    return render(request, 'users/student_signup.html', {'form': form})


def onstation_signup(request):
    form = OnStationSupervisorSignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:dashboard')
        messages.error(request, "Please fix the errors below.")
    return render(request, 'users/supervisor_signup.html', {'form': form, 'title': 'On-Station Supervisor Signup'})


def oncampus_signup(request):
    form = OnCampusSupervisorSignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:dashboard')
        messages.error(request, "Please fix the errors below.")
    return render(request, 'users/supervisor_signup.html', {'form': form, 'title': 'On-Campus Supervisor Signup'})


# ===== Dashboard Dispatcher =====

@login_required
def dashboard(request):
    role = getattr(request.user, 'role', None)
    if role == 'student':
        return redirect('users:student_dashboard')
    elif role == 'onstation':
        return redirect('users:onstation_dashboard')
    elif role == 'oncampus':
        return redirect('users:oncampus_dashboard')
    messages.error(request, "Your role is not recognized.")
    return render(request, 'users/dashboard.html')


# ===== Role-Specific Dashboards =====

@login_required
def student_dashboard(request):
    # Add any student specific info here if needed
    return render(request, 'users/student_dashboard.html')

from logbook.models import LogEntry  # make sure imported

@login_required
def oncampus_dashboard(request):
    user = request.user

    # Get students supervised by this on-campus supervisor
    students = StudentProfile.objects.filter(supervisor_oncampus__user=user)

    # Get user IDs of those students
    student_user_ids = students.values_list('user_id', flat=True)

    # Get all logs for those students (no filtering by status)
    logs = LogEntry.objects.filter(user_id__in=student_user_ids).order_by('-date')

    context = {
        'students': students,
        'logs': logs,
    }
    return render(request, 'users/oncampus_dashboard.html', context)

from django.shortcuts import get_object_or_404

@login_required
def onstation_dashboard(request):
    user = request.user
    return render(request, 'users/onstation_dashboard.html')


# ===== Profile Edit =====

@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('users:dashboard')
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def edit_student_profile(request):
    user = request.user
    try:
        student_profile = user.studentprofile
    except StudentProfile.DoesNotExist:
        student_profile = StudentProfile(user=user)

    if request.method == 'POST':
        user_form = ProfileForm(request.POST, request.FILES, instance=user)
        student_form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)

        if user_form.is_valid() and student_form.is_valid():
            user_form.save()
            student_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('users:dashboard')
        messages.error(request, "Please fix the errors below.")
    else:
        user_form = ProfileForm(instance=user)
        student_form = StudentProfileForm(instance=student_profile)

    return render(request, 'users/edit_student_profile.html', {
        'user_form': user_form,
        'student_form': student_form,
    })


# ===== Task Assignment =====

@login_required
def assign_task(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')
        task_title = request.POST.get('task_title')
        task_description = request.POST.get('task_description')
        due_date_str = request.POST.get('due_date')
        try:
            student_profile = CustomUser.objects.get(id=student_id).studentprofile
            due_date = date.fromisoformat(due_date_str) if due_date_str else date.today() + timedelta(days=7)
            AssignedTask.objects.create(
                student=student_profile,
                task_title=task_title,
                task_description=task_description,
                supervisor=request.user,
                due_date=due_date
            )
            messages.success(request, "Task assigned successfully.")
        except Exception as e:
            messages.error(request, f"Error assigning task: {e}")
    return redirect('users:dashboard')


@login_required
def bulk_assign_task(request):
    if request.method == 'POST':
        task_title = request.POST.get('task_title')
        task_description = request.POST.get('task_description')
        due_date_str = request.POST.get('due_date')
        due_date = date.fromisoformat(due_date_str) if due_date_str else date.today() + timedelta(days=7)
        students = CustomUser.objects.filter(role='student')
        for student in students:
            try:
                AssignedTask.objects.create(
                    student=student.studentprofile,
                    task_title=task_title,
                    task_description=task_description,
                    supervisor=request.user,
                    due_date=due_date
                )
            except Exception:
                continue
        messages.success(request, "Task assigned to all students successfully.")
    return redirect('users:dashboard')


# ===== Supervisor Document Upload =====

@login_required
def supervisor_upload_document(request):
    if request.method == 'POST':
        form = SupervisorUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_instance = form.save(commit=False)
            upload_instance.uploaded_by = request.user
            upload_instance.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect('users:dashboard')
        messages.error(request, "Please fix the errors below.")
    else:
        form = SupervisorUploadForm()
    return render(request, 'users/upload_department_resource.html', {'form': form})


# ===== View Student Profile & Logs =====

@login_required
def student_profile(request, pk):
    student_user = get_object_or_404(CustomUser, pk=pk, role='student')

    try:
        profile = student_user.studentprofile
    except StudentProfile.DoesNotExist:
        profile = None

    context = {
        'student': student_user,
        'profile': profile,
    }
    return render(request, 'users/student_profile.html', context)


@login_required
def supervisor_students(request, supervisor_id):
    supervisor_user = get_object_or_404(CustomUser, pk=supervisor_id)

    if supervisor_user.role not in ['onstation', 'oncampus']:
        return render(request, 'users/error.html', {'message': 'User is not a valid supervisor.'})

    if supervisor_user.role == 'onstation':
        try:
            onstation_supervisor = OnStationSupervisor.objects.get(user=supervisor_user)
        except OnStationSupervisor.DoesNotExist:
            return render(request, 'users/error.html', {'message': 'On-station supervisor record not found.'})
        students = StudentProfile.objects.filter(supervisor_onstation=onstation_supervisor)

    else:  # oncampus
        try:
            oncampus_supervisor = OnCampusSupervisor.objects.get(user=supervisor_user)
        except OnCampusSupervisor.DoesNotExist:
            return render(request, 'users/error.html', {'message': 'On-campus supervisor record not found.'})
        students = StudentProfile.objects.filter(supervisor_oncampus=oncampus_supervisor)

    context = {
        'supervisor': supervisor_user,
        'students': students,
    }
    return render(request, 'users/supervisor_students.html', context)


@login_required
def view_logs(request, student_id):
    student = get_object_or_404(CustomUser, pk=student_id, role='student')
    logs = LogEntry.objects.filter(student__user=student)
    return render(request, 'users/view_logs.html', {'logs': logs, 'student': student})


@login_required
def download_logs_pdf(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id)
    try:
        profile = student.studentprofile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('users:dashboard')

    logs = LogEntry.objects.filter(student__user=student).order_by('date')

    context = {
        'student': profile,
        'logs': logs,
    }

    template = get_template('users/logs_pdf_template.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.username}_logs.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response


@login_required
@require_POST
def bulk_approve_logs(request, student_id):
    LogEntry.objects.filter(student__user__id=student_id, status='pending').update(status='approved')
    messages.success(request, "All logs approved successfully.")
    return redirect('users:oncampus_dashboard')


@login_required
@require_POST
def bulk_reject_logs(request, student_id):
    LogEntry.objects.filter(student__user__id=student_id, status='pending').update(status='rejected')
    messages.success(request, "All logs rejected successfully.")
    return redirect('users:oncampus_dashboard')


@login_required
def message_supervisor(request, supervisor_id):
    supervisor = get_object_or_404(User, id=supervisor_id, role='onstation')
    return render(request, 'users/message_supervisor.html', {'supervisor': supervisor})


# ===== Assign Task to Multiple Students (for on-campus supervisors) =====

@login_required
def assign_task_to_students(request):
    if request.user.role != 'oncampus':
        return HttpResponseForbidden("You do not have permission to assign tasks.")

    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        task_description = request.POST.get('task_description')
        due_date_str = request.POST.get('due_date')

        if not student_ids or not task_description or not due_date_str:
            messages.error(request, "Please fill all required fields.")
            return redirect('users:assign_task_to_students')

        try:
            due_date = date.fromisoformat(due_date_str)
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('users:assign_task_to_students')

        for sid in student_ids:
            try:
                student_profile = StudentProfile.objects.get(id=sid)
                AssignedTask.objects.create(
                    student=student_profile,
                    task_description=task_description,
                    due_date=due_date,
                    supervisor=request.user
                )
            except Exception:
                continue

        messages.success(request, "Task(s) assigned successfully.")
        return redirect('users:assign_task_to_students')

    # GET request
    students = StudentProfile.objects.filter(supervisor_oncampus__user=request.user)
    assigned_tasks = AssignedTask.objects.filter(student__in=students).order_by('-due_date')

    return render(request, 'users/assign_task_to_students.html', {
        'students': students,
        'assigned_tasks': assigned_tasks,
    })


# ===== Track Progress =====

@login_required
def track_progress(request):
    students = StudentProfile.objects.all()
    progress_data = []

    for student in students:
        total_logs = LogEntry.objects.filter(student=student).count()
        approved_logs = LogEntry.objects.filter(student=student, status='approved').count()
        progress_percent = (approved_logs / total_logs * 100) if total_logs else 0
        progress_data.append({
            'student': student,
            'total_logs': total_logs,
            'approved_logs': approved_logs,
            'progress_percent': round(progress_percent, 2),
        })

    return render(request, 'users/track_progress.html', {'progress_data': progress_data})


# ===== Upload Department Resource =====

@login_required
def upload_department_resource(request):
    if request.method == 'POST':
        form = SupervisorUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_instance = form.save(commit=False)
            upload_instance.uploaded_by = request.user
            upload_instance.save()
            messages.success(request, "Resource uploaded successfully.")
            return redirect('users:dashboard')
        messages.error(request, "Please correct the errors below.")
    else:
        form = SupervisorUploadForm()

    return render(request, 'users/upload_department_resource.html', {'form': form})

from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import StudentProfile, AssignedTask

@login_required
def supervisor_assign_task(request):
    if request.user.role != 'oncampus':
        return HttpResponseForbidden("You do not have permission to assign tasks.")

    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        task_description = request.POST.get('task_description')
        due_date_str = request.POST.get('due_date')

        if not student_ids or not task_description or not due_date_str:
            messages.error(request, "Please fill all required fields.")
            return redirect('users:supervisor_assign_task')

        try:
            due_date = date.fromisoformat(due_date_str)
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('users:supervisor_assign_task')

        for sid in student_ids:
            try:
                student_profile = StudentProfile.objects.get(id=sid)
                AssignedTask.objects.create(
                    student=student_profile,
                    task_description=task_description,
                    due_date=due_date,
                    supervisor=request.user
                )
            except StudentProfile.DoesNotExist:
                continue

        messages.success(request, "Task(s) assigned successfully.")
        return redirect('users:supervisor_assign_task')

    students = StudentProfile.objects.filter(supervisor_oncampus__user=request.user)
    assigned_tasks = AssignedTask.objects.filter(student__in=students).order_by('-due_date')

    return render(request, 'users/assign_task_to_students.html', {
        'students': students,
        'assigned_tasks': assigned_tasks,
    })

@login_required
def logbook_activity(request):
    # your logic here
    return render(request, 'users/logbook_activity.html')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def logbook_activity(request):
    # Logic to show logbook activities
    return render(request, 'users/logbook_activity.html')

@login_required
def pending_logs(request):
    # Logic to show pending logs for supervisor approval
    return render(request, 'logbook/pending_logs.html')

@login_required
def approved_logs(request):
    # Logic to show approved logs
    return render(request, 'logbook/approve_logs.html')

@login_required
def approve_logs(request):
    # Page to approve logs with comments or bulk approve
    return render(request, 'logbook/approve_logs.html')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from logbook.models import LogEntry
from .models import StudentProfile

@login_required
def view_log_statistics(request):
    # Example stats:
    students = StudentProfile.objects.filter(supervisor_onstation__user=request.user)
    total_logs = 0
    pending_logs = 0
    approved_logs = 0

    for student in students:
        logs = LogEntry.objects.filter(student=student)
        total_logs += logs.count()
        pending_logs += logs.filter(status='pending').count()
        approved_logs += logs.filter(status='approved').count()

    context = {
        'total_logs': total_logs,
        'pending_logs': pending_logs,
        'approved_logs': approved_logs,
        'students': students,
    }
    return render(request, 'users/log_statistics.html', context)
