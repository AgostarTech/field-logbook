from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('approve/<int:log_id>/', views.approve_log, name='approve_log'),
    
]
