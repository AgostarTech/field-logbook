from django.urls import path
from .views import notification_history

urlpatterns = [
    path('history/', notification_history, name='notification_history'),
]
