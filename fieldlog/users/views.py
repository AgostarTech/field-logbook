from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User  # Using default User model

from .forms import (
    StudentSignUpForm,
    OnStationSupervisorSignUpForm,
    OnCampusSupervisorSignUpForm,
    ProfileForm,
)


# Home page
def home(request):
    return render(request, 'users/home.html')


# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'users/login.html')


# Signup selection page (choose role)
def signup_select(request):
    return render(request, 'users/signup_select.html')


# Student Signup view
def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentSignUpForm()

    return render(request, 'users/student_signup.html', {'form': form})


# On-Station Supervisor Signup
def onstation_signup(request):
    if request.method == 'POST':
        form = OnStationSupervisorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = OnStationSupervisorSignUpForm()

    return render(request, 'users/supervisor_signup.html', {
        'form': form,
        'title': 'On-Station Supervisor Signup'
    })


# On-Campus Supervisor Signup
def oncampus_signup(request):
    if request.method == 'POST':
        form = OnCampusSupervisorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = OnCampusSupervisorSignUpForm()

    return render(request, 'users/supervisor_signup.html', {
        'form': form,
        'title': 'On-Campus Supervisor Signup'
    })


# Dashboard view - role based
@login_required
def dashboard(request):
    role = getattr(request.user, 'role', None)
    if role == 'student':
        return render(request, 'users/student_dashboard.html')
    elif role in ['onstation', 'oncampus']:
        return render(request, 'users/supervisor_dashboard.html')
    else:
        return render(request, 'users/dashboard.html')  # fallback


# Profile edit view
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('logbook:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': foram})
