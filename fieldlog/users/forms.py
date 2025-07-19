from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from .models import (
    CustomUser,
    SupervisorProfile,
    StudentProfile,
    SupervisorUpload,
    AssignedTask,
)

# ==========================
# STUDENT SIGN UP FORM
# ==========================
class StudentSignUpForm(UserCreationForm):
    registration_number = forms.CharField(max_length=30, label="Registration Number")
    course = forms.CharField(max_length=100)
    year_of_study = forms.IntegerField(min_value=1, max_value=6, label="Year of Study")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_year_of_study(self):
        year = self.cleaned_data.get('year_of_study')
        if year is None:
            raise forms.ValidationError("Year of study is required.")
        if not (1 <= year <= 6):
            raise forms.ValidationError("Year of study must be between 1 and 6.")
        return year

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
# BASE SUPERVISOR SIGN UP FORM
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
# ON-STATION SUPERVISOR SIGN UP FORM
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
# ON-CAMPUS SUPERVISOR SIGN UP FORM
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
# PROFILE UPDATE FORM
# ==========================
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_picture']


# ==========================
# SUPERVISOR FILE UPLOAD FORM
# ==========================
class SupervisorUploadForm(forms.ModelForm):
    class Meta:
        model = SupervisorUpload
        fields = ['title', 'description', 'file']


# ==========================
# ASSIGN TASK FORM
# ==========================
class AssignedTaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Task Deadline"
    )

    class Meta:
        model = AssignedTask
        fields = ['task_title', 'task_description', 'due_date', 'student']

    def __init__(self, *args, **kwargs):
        supervisor = kwargs.pop('supervisor', None)
        super().__init__(*args, **kwargs)
        if supervisor:
            # Filter students supervised by this supervisor
            self.fields['student'].queryset = StudentProfile.objects.filter(
                models.Q(supervisor_oncampus__user=supervisor) |
                models.Q(supervisor_onstation__user=supervisor)
            ).distinct()
