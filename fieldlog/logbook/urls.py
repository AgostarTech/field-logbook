from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = "logbook"

urlpatterns = [
    # Dashboard
    path('student/', views.student_dashboard, name='student_dashboard'),
    

    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_update, name='edit_profile'),

    # Logbook Activities
    path('logs/', views.view_logs, name='view_logs'),
    path('logs/new/', views.new_logentry, name='new_logentry'),
    path('logs/create/', views.new_logentry, name='create_log_entry'),  # Could be merged logically
    path('logs/last/', views.view_last_entry, name='view_last_entry'),
    path('logs/update/', views.update_entry, name='update_entry'),
    path('add/', views.add_entry, name='add_entry'),
    path('edit/<int:pk>/', views.edit_entry, name='edit_entry'),
    path('detail/<int:pk>/', views.log_detail, name='log_detail'),

    # Progress Reporting
    path('progress-report/', views.progress_report_view, name='progress_report'),

    # Evaluation Forms
    path('evaluation-forms/', views.evaluation_forms_view, name='evaluation_forms'),

    # File Operations
    path('files/view/', views.view_files, name='view_files'),
    path('files/upload/', views.upload_file, name='upload_file'),
    path('files/download/', views.download_files, name='download_files'),
    path('files/delete/<int:file_id>/', views.delete_file, name='delete_file'),

    # Task Management
    path('tasks/assign/', views.assign_task, name='assign_task'),
    path('complete-task/<int:pk>/', views.mark_task_complete, name='mark_task_complete'),

    # Additional Functionalities
    path('ajax/get_institutions/', views.get_institutions, name='get_institutions'),
    path('add-entry/', views.add_entry_view, name='add_entry_view'),
    path('detail/<int:pk>/', views.log_detail, name='log_detail'),


    # Authentication
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
