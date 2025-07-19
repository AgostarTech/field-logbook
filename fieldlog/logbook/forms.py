from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm

from users.models import CustomUser
from .models import StudentProfile, LogEntry, UploadedFile, Task


# =========================
# Student Sign Up Form
# =========================

class StudentSignUpForm(UserCreationForm):
    academic_year = forms.CharField(max_length=20, required=True)
    registration_number = forms.CharField(max_length=30, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True  # Optional
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                course='Unknown',
                registration_number=self.cleaned_data.get('registration_number'),
                year_of_study=self.cleaned_data.get('academic_year'),
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

from django import forms
from .models import StudentProfile

class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['registration_number', 'year_of_study']  # Use correct field names here
        widgets = {
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control'}),
        }

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

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

class LogEntryForm(forms.ModelForm):
    class Meta:
        model = LogEntry
        fields = [
            'place', 'institution', 'date',
            'start_time', 'departure_time',
            'description', 'trainee_signature'
        ]
        widgets = {
            'place': forms.Select(attrs={'class': 'form-select'}),
            'institution': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5,
                'placeholder': 'Describe your daily tasks/assignments',
            }),
            'trainee_signature': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type your full name as signature',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['institution'].queryset = self.fields['institution'].queryset.none()

        if 'place' in self.data:
            try:
                place_id = int(self.data.get('place'))
                self.fields['institution'].queryset = self.fields['institution'].queryset.filter(place_id=place_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.place:
            self.fields['institution'].queryset = self.fields['institution'].queryset.filter(place=self.instance.place)


# =========================
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
