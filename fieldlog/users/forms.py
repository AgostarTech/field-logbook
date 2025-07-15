from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, SupervisorProfile, StudentProfile


# ==========================
# Student Sign Up Form
# ==========================
class StudentSignUpForm(UserCreationForm):
    registration_number = forms.CharField(max_length=30, label="Registration Number")
    course = forms.CharField(max_length=100)
    year_of_study = forms.IntegerField(min_value=1, label="Year of Study")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                registration_number=self.cleaned_data['registration_number'],
                course=self.cleaned_data['course'],
                year_of_study=self.cleaned_data['year_of_study'],
            )
        return user


# ==========================
# Base Supervisor Sign Up Form (Reusable)
# ==========================
class BaseSupervisorSignUpForm(UserCreationForm):
    department = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''


# ==========================
# On-Station Supervisor Sign Up
# ==========================
class OnStationSupervisorSignUpForm(BaseSupervisorSignUpForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'onstation'
        if commit:
            user.save()
            SupervisorProfile.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                phone=self.cleaned_data['phone'],
            )
        return user


# ==========================
# On-Campus Supervisor Sign Up
# ==========================
class OnCampusSupervisorSignUpForm(BaseSupervisorSignUpForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'oncampus'
        if commit:
            user.save()
            SupervisorProfile.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                phone=self.cleaned_data['phone'],
            )
        return user


# ==========================
# Profile Edit Form for All Users
# ==========================
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture', 'phone_number', 'email', 'first_name', 'last_name']
