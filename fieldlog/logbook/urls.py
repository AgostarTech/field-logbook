from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "logbook"  # Namespace for this app's URLs

urlpatterns = [
    # Profile Management
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_update, name='edit_profile'),

    # Logbook Activities
    path('log-activity/', views.log_activity_view, name='log_activity'),
    path('log-activity/create/', views.create_entry, name='create_log_entry'),
    path('log-activity/last/', views.view_last_entry, name='view_last_entry'),
    path('log-activity/update/', views.update_entry, name='update_entry'),

    # Progress Reporting
    path('progress-report/', views.progress_report_view, name='progress_report'),

    # Evaluation Forms
    path('evaluation-forms/', views.evaluation_forms_view, name='evaluation_forms'),

    # File Operations
    path('files/view/', views.view_files, name='view_files'),
    path('files/upload/', views.upload_file, name='upload_file'),
    path('files/download/', views.download_files, name='download_files'),
    path('files/delete/<int:file_id>/', views.delete_file, name='delete_file'),

    # New Log Entry with automatic day counting
    path('new/', views.new_logentry, name='new_logentry'),

    # AJAX: Dynamic institution fetch
    path('ajax/get_institutions/', views.get_institutions, name='get_institutions'),

    # Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
