from django.urls import path
from .views import ai_recommendation

urlpatterns = [
    path('ask/', ai_recommendation, name='ai_recommendation'),
]
