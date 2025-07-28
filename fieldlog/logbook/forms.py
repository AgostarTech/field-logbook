from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from users.models import CustomUser
from .models import StudentProfile, LogEntry, UploadedFile, Task

User = get_user_model()


# =========================
# Student Sign Up Form
# =========================

class StudentSignUpForm(UserCreationForm):
    academic_year = forms.CharField(max_length=20, required=True)
    registration_number = forms.CharField(max_length=30, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def clean_registration_number(self):
        reg_no = self.cleaned_data.get('registration_number')
        if StudentProfile.objects.filter(registration_number=reg_no).exists():
            raise ValidationError("This registration number is already used by another student.")
        return reg_no

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                academic_year=self.cleaned_data.get('academic_year'),
                registration_number=self.cleaned_data.get('registration_number'),
            )
        return user


# =========================
# User Profile Update Forms
# =========================

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['registration_number', 'year_of_study']  # adjust if needed
        widgets = {
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'profile_picture']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# =========================
# Log Entry Form
# =========================

from django import forms
from .models import LogEntry
from django.utils.timezone import now

class LogEntryForm(forms.ModelForm):
    class Meta:
        model = LogEntry
        fields = [
            'date',
            'start_time',
            'departure_time',
            'description',
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control mb-3',
                'value': now().date(),
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control mb-3',
            }),
            'departure_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control mb-3',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control notebook-style mb-3',
                'rows': 6,
                'placeholder': 'Describe your daily tasks/assignments',
            }),
        }



# File Upload Form
# =========================

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# =========================
# Weekly Progress Report Form
# =========================

class ProgressReportForm(forms.Form):
    supervisor_comment_week_1 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Supervisor comments for Week 1'
        })
    )
    supervisor_comment_week_2 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Supervisor comments for Week 2'
        })
    )
    supervisor_comment_week_3 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Supervisor comments for Week 3'
        })
    )
    supervisor_comment_week_4 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Supervisor comments for Week 4'
        })
    )
    supervisor_comment_week_5 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Supervisor comments for Week 5'
        })
    )

    latitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)


# =========================
# Task Assignment Form
# =========================

class TaskAssignForm(forms.Form):
    task_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Write task here...'
        }),
        label="Task Description",
        required=True
    )
    student_ids = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Select Students",
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['student_ids'].queryset = StudentProfile.objects.filter(supervisor=user)

from django import forms
from .models import StudentProfile

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'profile_picture',
            'phone_number',
            'registration_number',
            'course',
            'year_of_study',
            'academic_year',
            'field_start_date',
            'organization_name',
            'supervisor',
        ]
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration Number'}),
            'course': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Academic Year (e.g., 2024/2025)'}),
            'field_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization Name'}),
            'supervisor': forms.Select(attrs={'class': 'form-select'}),
        }
