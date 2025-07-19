from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import get_template
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa

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

User = get_user_model()

# ----- Basic Views -----

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
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')


def signup_select(request):
    return render(request, 'users/signup_select.html')


# ----- Signup Views -----

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import StudentSignUpForm

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        print("POST data:", request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:dashboard')
        else:
            print("Form errors:", form.errors)
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
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    return render(request, 'users/supervisor_signup.html', {'form': form, 'title': 'On-Station Supervisor Signup'})


def oncampus_signup(request):
    form = OnCampusSupervisorSignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    return render(request, 'users/supervisor_signup.html', {'form': form, 'title': 'On-Campus Supervisor Signup'})


# ----- Dashboard Dispatcher -----

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


# ----- Role Specific Dashboards -----

@login_required
def student_dashboard(request):
    return render(request, 'users/student_dashboard.html')


@login_required
def onstation_dashboard(request):
    user = request.user
    assigned_students = User.objects.filter(role='student', studentprofile__supervisor_onstation__user=user)
    logs = LogEntry.objects.filter(student__user__in=assigned_students)

    student_progress = []
    for student in assigned_students:
        total_logs = logs.filter(student__user=student).count()
        approved_logs_count = logs.filter(student__user=student, status='approved').count()
        progress_percent = (approved_logs_count / total_logs * 100) if total_logs else 0
        student_progress.append({
            'student': student,
            'total_logs': total_logs,
            'approved_logs': approved_logs_count,
            'progress_percent': round(progress_percent, 2),
        })

    context = {
        'assigned_students': assigned_students,
        'student_progress': student_progress,
        'pending_logs': logs.filter(status='pending'),
        'approved_logs': logs.filter(status='approved'),
        'assigned_tasks': AssignedTask.objects.filter(supervisor=user),
    }
    return render(request, 'users/supervisor_dashboard.html', context)


@login_required
def oncampus_dashboard(request):
    user = request.user
    if user.role != 'oncampus':
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')

    # Students under the same department
    students = User.objects.filter(role='student', department=user.department)
    student_profiles = StudentProfile.objects.filter(user__in=students)

    # On-station supervisors in the same department
    supervisors = User.objects.filter(role='onstation', department=user.department)

    # Get logs from those student profiles
    logs = LogEntry.objects.filter(student__in=student_profiles)

    # Build progress data
    progress_data = []
    for profile in student_profiles:
        student_logs = logs.filter(student=profile)
        last_log = student_logs.order_by('-date').first()
        progress_data.append({
            'student': profile.user,
            'registration_number': profile.registration_number,
            'total_logs': student_logs.count(),
            'approved_logs': student_logs.filter(status='approved').count(),
            'pending_logs': student_logs.filter(status='pending').count(),
            'rejected_logs': student_logs.filter(status='rejected').count(),
            'last_submission_date': last_log.date if last_log else None,
        })

    context = {
        'department_students': students,
        'onstation_supervisors': supervisors,
        'progress_data': progress_data,
        'submitted_logs': logs.count(),
        'approved_logs': logs.filter(status='approved').count(),
        'pending_logs': logs.filter(status='pending').count(),
        'rejected_logs': logs.filter(status='rejected').count(),
    }

    return render(request, 'users/oncampus_dashboard.html', context)


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('dashboard')
    return render(request, 'users/edit_profile.html', {'form': form})


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
    return redirect('dashboard')


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
    return redirect('dashboard')


@login_required
def supervisor_upload_document(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        if not title or not file:
            messages.error(request, "Title and file are required.")
            return redirect('dashboard')
        SupervisorUpload.objects.create(title=title, file=file, uploaded_by=request.user)
        messages.success(request, "Document uploaded successfully.")
    return redirect('dashboard')


# ----- View Student and Supervisor Info -----

@login_required
def student_profile(request, pk):
    student_user = get_object_or_404(CustomUser, pk=pk, role='student')
    return render(request, 'users/student_profile.html', {'student': student_user})


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


# ----- Logs Views -----

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
        return redirect('dashboard')

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
    return redirect('oncampus_dashboard')


@login_required
@require_POST
def bulk_reject_logs(request, student_id):
    LogEntry.objects.filter(student__user__id=student_id, status='pending').update(status='rejected')
    messages.success(request, "All logs rejected successfully.")
    return redirect('oncampus_dashboard')


@login_required
def message_supervisor(request, supervisor_id):
    supervisor = get_object_or_404(User, id=supervisor_id, role='onstation')
    return render(request, 'users/message_supervisor.html', {'supervisor': supervisor})


# ----- Assign Task to Multiple Students (for on-campus supervisors) -----

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
            return redirect('assign_task_to_students')

        try:
            due_date = date.fromisoformat(due_date_str)
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('assign_task_to_students')

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
        return redirect('assign_task_to_students')

    # GET request
    students = StudentProfile.objects.filter(oncampus_supervisor=request.user)
    assigned_tasks = AssignedTask.objects.filter(student__in=students).order_by('-due_date')

    return render(request, 'users/assign_task_to_students.html', {
        'students': students,
        'assigned_tasks': assigned_tasks,
    })


# ----- Track Progress -----

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


# ----- Upload Department Resource -----

@login_required
def upload_department_resource(request):
    if request.method == 'POST':
        form = SupervisorUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_instance = form.save(commit=False)
            upload_instance.uploaded_by = request.user
            upload_instance.save()
            messages.success(request, "Resource uploaded successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SupervisorUploadForm()

    return render(request, 'users/upload_department_resource.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def supervisor_assign_task(request):
    # You can later add your logic here
    return render(request, 'users/supervisor_assign_task.html')
