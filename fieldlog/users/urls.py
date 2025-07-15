from django.urls import path
from django.contrib.auth import views as auth_views  # 🔹 Import built-in views
from . import views
from .views import (
    student_signup,
    onstation_signup,
    oncampus_signup,
    signup_select
)

urlpatterns = [
    path('', views.home, name='home'),  # Default home page
    path('login/', views.login_view, name='login'),  # Custom login
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # ✅ Built-in logout

    # Signup options
    path('signup/', signup_select, name='signup_select'),
    path('signup/student/', student_signup, name='student_signup'),
    path('signup/onstation/', onstation_signup, name='onstation_signup'),
    path('signup/oncampus/', oncampus_signup, name='oncampus_signup'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]
