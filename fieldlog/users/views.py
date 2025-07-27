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
import logging
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Max
from django.utils import timezone

from .models import (
    StudentProfile,
    OnStationSupervisor,
    LogEntry,
    TaskResource,
)
from users.models import CustomUser  # If you need to list all oncampus users later


logger = logging.getLogger(__name__)



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



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Max
from django.utils import timezone

@login_required
def oncampus_dashboard(request):
    user = request.user

    # Only allow On-Campus Supervisors
    if user.role != 'oncampus':
        return redirect('login')

    department = user.department
    total_required_logs = 60

    # Get search and filter query params
    search_query = request.GET.get('q', '')
    progress_filter = request.GET.get('progress_filter', '')

    # Get all students in department or all if no department assigned
    if department:
        department_students = StudentProfile.objects.filter(department=department.name).select_related('user')
    else:
        department_students = StudentProfile.objects.all().select_related('user')

    # Apply search filters if any
    if search_query:
        department_students = department_students.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(registration_number__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Enrich each student with log progress info
    enriched_students = []
    for student in department_students:
        # Use the StudentProfile instance directly
        student_logs = LogEntry.objects.filter(student=student)

        approved_count = student_logs.filter(status='approved').count()
        pending_count = student_logs.filter(status='pending').count()
        progress = round((approved_count / total_required_logs) * 100, 1) if total_required_logs else 0

        student.progress = progress
        student.logs_submitted = approved_count
        student.pending_logs = pending_count
        student.email = getattr(student.user, 'email', '')
        student.phone = getattr(student.user, 'phone_number', '')
        enriched_students.append(student)

    # Filter students by progress range if filter applied
    if progress_filter in ['0-25', '26-50', '51-75', '76-100']:
        ranges = {
            '0-25': (0, 25),
            '26-50': (26, 50),
            '51-75': (51, 75),
            '76-100': (76, 100),
        }
        min_val, max_val = ranges[progress_filter]
        enriched_students = [s for s in enriched_students if min_val <= s.progress <= max_val]

    # Summary stats
    department_students_count = len(enriched_students)
    submitted_logs = sum(s.logs_submitted for s in enriched_students)
    pending_logs = sum(s.pending_logs for s in enriched_students)

    # On-Station Supervisors assigned to students under this On-Campus supervisor
    assigned_students = StudentProfile.objects.filter(supervisor_oncampus__user=user)
    supervisor_ids = assigned_students.values_list('supervisor_onstation__user_id', flat=True).distinct()
    onstation_supervisors = OnStationSupervisor.objects.filter(user_id__in=supervisor_ids).select_related('user')

    for sup in onstation_supervisors:
        sup.assigned_students_count = StudentProfile.objects.filter(supervisor_onstation=sup).count()
        sup.email = getattr(sup.user, 'email', '')
        sup.phone = getattr(sup.user, 'phone_number', '')

    total_supervisors = onstation_supervisors.count()

    # Aggregate log data for progress charts or summary
    user_ids = [s.user.id for s in enriched_students]
    progress_data = LogEntry.objects.filter(student__user__id__in=user_ids).values(
        'student__user__id',
        'student__user__first_name',
        'student__user__last_name',
    ).annotate(
        total=Count('id'),
        approved=Count('id', filter=Q(status='approved')),
        pending=Count('id', filter=Q(status='pending')),
        overdue=Count('id', filter=Q(status='pending', date__lt=timezone.now())),
        last_submission_date=Max('date'),
    )

    # Tasks and resources assigned for the department
    tasks_and_resources = TaskResource.objects.filter(
        department=department
    ).prefetch_related('assigned_to').order_by('-created_at') if department else TaskResource.objects.all().order_by('-created_at')

    # Selected student display logic from GET param
    selected_student_id = request.GET.get('student_id')
    selected_profile = None
    student_user = None
    logs = []

    if selected_student_id:
        try:
            selected_profile = next(s for s in enriched_students if str(s.user.id) == selected_student_id)
        except StopIteration:
            selected_profile = enriched_students[0] if enriched_students else None
    elif enriched_students:
        selected_profile = enriched_students[0]

    if selected_profile:
        student_user = selected_profile.user
        logs = LogEntry.objects.filter(student=selected_profile).order_by('-date')

    # Handle marks update POST
    if request.method == 'POST' and selected_profile:
        performance_mark = request.POST.get('performance')
        try:
            mark = float(performance_mark)
            if 0 <= mark <= 100:
                selected_profile.marks = mark
                selected_profile.save()
        except ValueError:
            pass
        return redirect(f"{request.path}?student_id={selected_profile.user.id}")

    context = {
        'assigned_students': assigned_students,
        'department_students': enriched_students,
        'department_students_count': department_students_count,
        'submitted_logs': submitted_logs,
        'pending_logs': pending_logs,
        'total_supervisors': total_supervisors,
        'onstation_supervisors': onstation_supervisors,
        'progress_data': progress_data,
        'tasks_and_resources': tasks_and_resources,
        'student': student_user,
        'profile': selected_profile,
        'logs': logs,
    }

    return render(request, 'users/oncampus_dashboard.html', context)




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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, Max
from .models import StudentProfile, LogEntry, TaskResource, OnStationSupervisor, OnCampusSupervisor

@login_required
def student_profile(request, pk):
    # Get the student user
    student_user = get_object_or_404(CustomUser, pk=pk, role='student')

    # Get student profile
    try:
        profile = student_user.studentprofile
    except StudentProfile.DoesNotExist:
        profile = None

    # Logs
    logs = LogEntry.objects.filter(user=student_user).order_by('-date')
    total_logs = logs.count()
    approved_logs = logs.filter(approved=True).count()
    pending_logs = logs.filter(approved=False).count()
    last_log_date = logs.aggregate(last=Max('date'))['last']

    # Progress
    total_required_logs = 60
    progress = round((approved_logs / total_required_logs) * 100, 1) if total_required_logs else 0

    # Course (handle ForeignKey, ManyToMany or plain field)
    if hasattr(profile, 'course'):
        try:
            course = profile.course.all() if hasattr(profile.course, 'all') else [profile.course]
            course_names = ', '.join([c.name for c in course])
        except Exception:
            course_names = getattr(profile, 'course', 'N/A')
    else:
        course_names = 'N/A'

    # Supervisors
    onstation_supervisor = getattr(profile, 'supervisor_onstation', None)
    oncampus_supervisor = getattr(profile, 'supervisor_oncampus', None)

    # Department
    department = getattr(student_user, 'department', None)

    # Tasks assigned to this student
    assigned_tasks = TaskResource.objects.filter(assigned_to=student_user)

    context = {
        'student': student_user,
        'profile': profile,
        'logs': logs,
        'total_logs': total_logs,
        'approved_logs': approved_logs,
        'pending_logs': pending_logs,
        'last_log_date': last_log_date,
        'progress': progress,
        'course_names': course_names,
        'onstation_supervisor': onstation_supervisor,
        'oncampus_supervisor': oncampus_supervisor,
        'department': department,
        'assigned_tasks': assigned_tasks,
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
    # Only On-Campus Supervisors can assign tasks
    if request.user.role != 'oncampus':
        return HttpResponseForbidden("You do not have permission to assign tasks.")

    # Get all students in this supervisor's department or assigned to them
    # Adjust the filter as per your model relationships
    students = StudentProfile.objects.filter(department=request.user.department)

    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        task_description = request.POST.get('task_description', '').strip()
        due_date_str = request.POST.get('due_date', '').strip()

        # Basic validation
        if not student_ids or not task_description or not due_date_str:
            messages.error(request, "Please fill all required fields.")
            return redirect('users:assign_task_to_students')

        try:
            due_date = date.fromisoformat(due_date_str)
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('users:assign_task_to_students')

        # Assign tasks inside a transaction for safety
        try:
            with transaction.atomic():
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
                        logger.warning(f"StudentProfile with id={sid} does not exist.")
                    except Exception as e:
                        logger.error(f"Error assigning task to student id={sid}: {e}")
            messages.success(request, "Task(s) assigned successfully.")
        except Exception as e:
            logger.error(f"Failed to assign tasks transactionally: {e}")
            messages.error(request, "An error occurred while assigning tasks. Please try again.")

        return redirect('users:assign_task_to_students')

    # GET request: render the form with available students
    context = {
        'students': students,
    }
    return render(request, 'users/assign_task_to_students.html', context)

# ===== Track Progress =====
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from logbook.models import LogEntry  # Make sure this import exists
from users.models import StudentProfile  # Adjust if your model is in another location

@login_required
def track_progress(request):
    students = StudentProfile.objects.all()
    progress_data = []

    for student in students:
        total_logs = LogEntry.objects.filter(student=student).count()
        approved_logs = LogEntry.objects.filter(student=student, status='approved').count()  # or status=True, depending on your model

        progress_percent = (approved_logs / total_logs * 100) if total_logs else 0

        progress_data.append({
            'student': student,
            'total_logs': total_logs,
            'approved_logs': approved_logs,
            'progress_percent': round(progress_percent, 2),
        })

    return render(request, 'users/track_progress.html', {'progress_data': progress_data})





# ===== Upload Department Resource =====
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

@login_required
def upload_department_resource(request):
    # Optional: Restrict upload permission only to supervisors (adjust role name as needed)
    if request.user.role != 'oncampus':
        return HttpResponseForbidden("You do not have permission to upload resources.")

    if request.method == 'POST':
        form = SupervisorUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_instance = form.save(commit=False)
            upload_instance.uploaded_by = request.user
            upload_instance.save()
            messages.success(request, "Resource uploaded successfully.")
            return redirect('users:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SupervisorUploadForm()

    context = {'form': form}
    return render(request, 'users/upload_department_resource.html', context)

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




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from users.models import DepartmentResource  # Only import DepartmentResource

@login_required
def view_uploaded_resources(request):
    # Query all uploaded department resources
    department_resources = DepartmentResource.objects.select_related('uploaded_by').all()

    # Prepare resource list with source tag
    all_resources = []
    for res in department_resources:
        all_resources.append({
            'title': res.title,
            'file': res.file,
            'uploaded_by': res.uploaded_by,
            'uploaded_at': res.uploaded_at,
            'source': 'Department',
        })

    # Sort by uploaded_at descending
    all_resources.sort(key=lambda x: x['uploaded_at'], reverse=True)

    context = {
        'resources': all_resources,
    }

    return render(request, 'users/view_uploaded_resources.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import StudentProfile, OnStationSupervisor, OnCampusSupervisor

@login_required
def view_all_students(request):
    students = StudentProfile.objects.select_related('user').all()
    return render(request, 'users/view_all_students.html', {'students': students})

@login_required
def view_all_onstation_supervisors(request):
    supervisors = OnStationSupervisor.objects.select_related('user').all()
    return render(request, 'users/view_all_onstation_supervisors.html', {'supervisors': supervisors})

@login_required
def view_all_oncampus_supervisors(request):
    supervisors = OnCampusSupervisor.objects.select_related('user').all()
    return render(request, 'users/view_all_oncampus_supervisors.html', {'supervisors': supervisors})

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import StudentProfile

@login_required
def download_uploaded_documents(request, student_id):
    student = get_object_or_404(StudentProfile, user__id=student_id)
    # Example: Assuming you store documents in MEDIA_ROOT/students/{student_id}/
    documents_dir = os.path.join(settings.MEDIA_ROOT, 'students', str(student.user.id))

    # Your logic to zip documents and send as response
    # This is a simplified placeholder:
    if not os.path.exists(documents_dir):
        raise Http404("Documents not found")

    # For demo, just return an empty response or a dummy file
    response = HttpResponse("Documents download functionality to be implemented.", content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="student_{student.user.id}_documents.zip"'
    return response
import os
from django.shortcuts import get_object_or_404, redirect
from django.http import FileResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from .models import StudentProfile, UploadedDocument

def _serve_file(filepath, download_name=None):
    """
    Helper function to serve a file if it exists, or raise 404.
    """
    if filepath and os.path.exists(filepath):
        filename = download_name or os.path.basename(filepath)
        return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404("File not found.")

def download_general_report(request, student_id):
    student = get_object_or_404(StudentProfile, user__id=student_id)
    if not student.general_report:
        raise Http404("General report not found.")
    return _serve_file(student.general_report.path, download_name=f"{student.user.get_full_name()}_general_report.pdf")

def download_technical_report(request, student_id):
    student = get_object_or_404(StudentProfile, user__id=student_id)
    if not student.technical_report:
        raise Http404("Technical report not found.")
    return _serve_file(student.technical_report.path, download_name=f"{student.user.get_full_name()}_technical_report.pdf")

def download_uploaded_documents(request, student_id):
    student = get_object_or_404(StudentProfile, user__id=student_id)
    documents = student.uploaded_documents.all()  # using related_name 'uploaded_documents'

    if not documents.exists():
        raise Http404("No uploaded documents found.")

    # For simplicity, download the first document
    doc = documents.first()
    if not doc.file:
        raise Http404("Document file not found.")
    extension = os.path.splitext(doc.file.name)[1]
    return _serve_file(doc.file.path, download_name=f"{student.user.get_full_name()}_{doc.title or 'document'}{extension}")

@require_http_methods(["POST"])
def assign_marks(request, student_id):
    student = get_object_or_404(StudentProfile, user__id=student_id)
    marks = request.POST.get('marks')

    if marks is None or marks == '':
        return HttpResponse("Marks value is required.", status=400)

    try:
        marks_value = float(marks)
    except ValueError:
        return HttpResponse("Marks must be a valid number.", status=400)

    if not (0 <= marks_value <= 100):
        return HttpResponse("Marks must be between 0 and 100.", status=400)

    student.marks = marks_value
    student.save()

    return redirect('users:oncampus_dashboard')

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StudentProfile, LogEntry

@login_required
def export_student_logs_pdf(request, student_id):
    student_profile = get_object_or_404(StudentProfile, pk=student_id)
    logs = LogEntry.objects.filter(student=student_profile).order_by('date')

    # Create the HttpResponse object with PDF headers.
    response = HttpResponse(content_type='application/pdf')
    filename = f"{student_profile.user.username}_logs.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create the PDF object, using the response as its "file."
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(inch, height - inch, f"Log Entries for {student_profile.user.get_full_name() or student_profile.user.username}")

    # Starting y position
    y = height - inch * 1.5
    line_height = 14

    p.setFont("Helvetica", 12)
    if not logs.exists():
        p.drawString(inch, y, "No log entries found.")
    else:
        for log in logs:
            # Stop if too many lines on one page (simple pagination)
            if y < inch:
                p.showPage()
                y = height - inch
                p.setFont("Helvetica", 12)

            date_str = log.date.strftime("%Y-%m-%d")
            status = log.status.capitalize()
            p.drawString(inch, y, f"Date: {date_str} | Status: {status}")
            y -= line_height

            # Wrap content text (very simple)
            content_lines = log.content.split('\n')
            for line in content_lines:
                # truncate very long lines
                if len(line) > 90:
                    line = line[:87] + "..."
                p.drawString(inch + 20, y, line)
                y -= line_height

            y -= line_height  # extra space between logs

    p.showPage()
    p.save()

    return response

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def all_students_logs(request):
    # Your logic to get all students' logs here
    logs = ...  # fetch logs, e.g. LogEntry.objects.all()
    context = {'logs': logs}
    return render(request, 'logbook/all_students_logs.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from users.models import CustomUser
import io
from reportlab.pdfgen import canvas

@login_required
def download_logs_pdf(request, student_id):
    # Pata student, toa 404 kama haipo
    student = get_object_or_404(CustomUser, id=student_id)

    # Fanya PDF generation
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Logs for {student.get_full_name()}")
    # ...ongeza data zaidi kutoka kwa logs zako...

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="logs_{student_id}.pdf"'
    return response
