from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from logbook.models import LogEntry
from .models import Task
from .forms import TaskForm
from users.models import CustomUser
from notifications.utils import send_notification_email

@login_required
def supervisor_dashboard(request):
    if request.user.role not in ['onstation', 'oncampus']:
        return redirect('dashboard')

    # See all student logs
    student_logs = LogEntry.objects.all().order_by('-date')
    task_form = TaskForm(request.POST or None)

    if request.method == 'POST' and task_form.is_valid():
        task = task_form.save(commit=False)
        task.supervisor = request.user
        task.save()
        return redirect('supervisor_dashboard')

    return render(request, 'supervisors/supervisor_dashboard.html', {
        'logs': student_logs,
        'form': task_form
    })

@login_required
def approve_log(request, log_id):
    if request.user.role not in ['onstation', 'oncampus']:
        return redirect('dashboard')

    log = get_object_or_404(LogEntry, id=log_id)
    log.approved = True
    log.save()

    # Notify the student their log was approved
    send_notification_email(
        subject="Your Field Log Was Approved",
        message=f"Your log entry for {log.date} was approved by your supervisor.",
        recipient_email=log.student.email
    )

    return redirect('supervisor_dashboard')
