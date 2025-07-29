from django.urls import path
from . import views

app_name = 'logbook'

urlpatterns = [
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),

    # Evaluation Forms
    path('evaluation-forms/', views.evaluation_forms_view, name='evaluation_forms'),

    # Log Entries
    path('log/new/', views.new_logentry, name='new_logentry'),
    path('log/last/', views.view_last_entry, name='view_last_entry'),
    path('log/create/', views.create_entry, name='create_entry'),
    path('log/update/', views.update_entry, name='update_entry'),
    path('log/edit/<int:pk>/', views.edit_entry, name='edit_entry'),
    path('log/detail/<int:pk>/', views.log_detail, name='log_detail'),

    # Log Actions (Download, Update, Comment, Delete)
    path('log/<int:pk>/download/', views.download_log, name='download_log'),
    path('log/<int:pk>/update/', views.update_log, name='update_log'),
    path('log/<int:pk>/comments/', views.log_comments, name='log_comments'),
    path('log/<int:pk>/delete/', views.delete_log, name='delete_log'),

    # Logs by Roles
    path('logs/', views.view_logs, name='view_logs'),
    path('logs/<int:student_id>/', views.view_logs, name='view_logs'),
    path('all-logs/', views.all_students_logs, name='all_students_logs'),
    path('student-logs/<int:student_id>/', views.student_logs, name='student_logs'),

    # AJAX: Institutions
    path('ajax/get-institutions/', views.get_institutions, name='get_institutions'),

    # Progress Reports
    path('progress-report/', views.progress_report_view, name='progress_report'),
    path('download-pdf/', views.download_entry_pdf, name='download_entry_pdf'),

    # Files
    path('files/', views.view_files, name='view_files'),
    path('files/upload/', views.upload_file, name='upload_file'),
    path('files/download/', views.download_files, name='download_files'),
    path('files/delete/<int:file_id>/', views.delete_file, name='delete_file'),

    # Signup
    path('signup/student/', views.student_signup, name='student_signup'),

    # Tasks
    path('tasks/assign/', views.assign_task, name='assign_task'),
    path('tasks/mark-complete/<int:pk>/', views.mark_task_complete, name='mark_task_complete'),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),

    # Log Profile
    path('log-profile/', views.get_log_profile_data, name='log_profile'),
    path('log-profile/<int:user_id>/', views.get_log_profile_data, name='log_profile_for_user'),

    # Entry Additions
    path('add-entry/', views.add_entry, name='add_entry'),
    path('add-entry-view/', views.add_entry_view, name='add_entry_view'),
    path('evaluation-forms/', views.evaluation_forms_view, name='evaluation_forms'),
]
