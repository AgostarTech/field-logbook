from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import export_student_logs_pdf

from .views import assign_task_to_students, track_progress

app_name = 'users'

urlpatterns = [
    # Home and Authentication
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Signup Options
    path('signup-select/', views.signup_select, name='signup_select'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('signup/onstation/', views.onstation_signup, name='onstation_signup'),
    path('signup/oncampus/', views.oncampus_signup, name='oncampus_signup'),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/onstation/', views.onstation_dashboard, name='onstation_dashboard'),
    path('dashboard/oncampus/', views.oncampus_dashboard, name='oncampus_dashboard'),

    # Profile Editing
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/edit/student/', views.edit_student_profile, name='edit_student_profile'),

    # Student Profile View
    path('student/<int:pk>/', views.student_profile, name='student_profile'),

    # Task Assignment
    path('assign-task/', views.assign_task, name='assign_task'),
    path('bulk-assign-task/', views.bulk_assign_task, name='bulk_assign_task'),
    path('supervisor/assign-task/', views.supervisor_assign_task, name='supervisor_assign_task'),
    path('dashboard/oncampus/assign-tasks/', assign_task_to_students, name='assign_task_to_students'),

    # Logbook Entries
    path('logs/<int:student_id>/', views.view_logs, name='view_logs'),
    path('view-logs/<int:student_id>/', views.view_logs, name='view_logs_alt'),
    path('download-logs/<int:student_id>/', views.download_logs_pdf, name='download_logs_pdf'),
    

    # File Upload by Supervisors
    path('supervisor/upload-document/', views.supervisor_upload_document, name='supervisor_upload_document'),
    path('dashboard/oncampus/upload-resource/', views.upload_department_resource, name='upload_department_resource'),

    # Supervisor Filters
    path('supervisor/<int:supervisor_id>/students/', views.supervisor_students, name='supervisor_students'),

    # Progress Tracking
    path('dashboard/oncampus/track-progress/', track_progress, name='track_progress'),

    # Bulk Log Approval
    path('logs/bulk-approve/<int:student_id>/', views.bulk_approve_logs, name='bulk_approve_logs'),
    path('logs/bulk-reject/<int:student_id>/', views.bulk_reject_logs, name='bulk_reject_logs'),

    # Messaging
    path('supervisor/<int:supervisor_id>/message/', views.message_supervisor, name='message_supervisor'),
    path('logbook-activity/', views.logbook_activity, name='logbook_activity'),

    # Pending and Approved Logs
    path('pending-logs/', views.pending_logs, name='pending_logs'),
    path('approved-logs/', views.approved_logs, name='approved_logs'),
    path('approve-logs/', views.approve_logs, name='approve_logs'),

    # Password Change Views
    path('password/change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change.html'), name='change_password'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
    path('log_statistics/', views.view_log_statistics, name='view_log_statistics'),

    path('view-resources/', views.view_uploaded_resources, name='view_uploaded_resources'),
    
    path('students/all/', views.view_all_students, name='view_all_students'),
    path('dashboard/oncampus/student/<int:student_id>/', views.oncampus_dashboard, name='oncampus_dashboard_student'),

    
    path('supervisors/onstation/', views.view_all_onstation_supervisors, name='view_all_onstation_supervisors'),
    path('supervisors/oncampus/', views.view_all_oncampus_supervisors, name='view_all_oncampus_supervisors'),

    # Download student documents and reports
    path('students/<int:student_id>/download-documents/', views.download_uploaded_documents, name='download_uploaded_documents'),
    path('students/<int:student_id>/download-general-report/', views.download_general_report, name='download_general_report'),
    path('students/<int:student_id>/download-technical-report/', views.download_technical_report, name='download_technical_report'),

    # Assign marks
    path('students/<int:student_id>/assign-marks/', views.assign_marks, name='assign_marks'),
    path('logs/<int:student_id>/', views.view_logs, name='view_logs'),

    
    path('export-logs/<int:student_id>/', export_student_logs_pdf, name='export_student_logs_pdf'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
