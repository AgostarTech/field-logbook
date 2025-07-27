from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import StudentProfile

from django.db import models
from .models import (
    CustomUser,
    SupervisorProfile,
    StudentProfile,
    OnStationSupervisor,
    SupervisorUpload,
    AssignedTask,
)

# ==========================
# STUDENT SIGN UP FORM
# ==========================
from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser, StudentProfile, Department, Course, SupervisorProfile

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

YEAR_CHOICES = [(i, str(i)) for i in range(1, 7)]
from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser, StudentProfile, Department, Course, SupervisorProfile

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

YEAR_CHOICES = [(i, str(i)) for i in range(1, 7)]

class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    middle_name = forms.CharField(max_length=30, required=False, label="Second Name")
    last_name = forms.CharField(max_length=30, required=True, label="Surname")
    
    registration_number = forms.CharField(max_length=30, required=True, label="Registration Number")
    
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False, label="Gender")
    
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False, empty_label="Select Course")
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, empty_label="Select Department")
    
    phone = forms.CharField(max_length=15, required=False, label="Phone Number")
    email = forms.EmailField(required=False, label="Email Address")
    
    year_of_study = forms.ChoiceField(choices=YEAR_CHOICES, required=False, label="Year of Study")
    
    onstation_supervisor = forms.ModelChoiceField(
        queryset=SupervisorProfile.objects.filter(user__role='onstation'),
        required=False, empty_label="Select On-Station Supervisor", label="On-Station Supervisor"
    )
    
    oncampus_supervisor = forms.ModelChoiceField(
        queryset=SupervisorProfile.objects.filter(user__role='oncampus'),
        required=False, empty_label="Select On-Campus Supervisor", label="On-Campus Supervisor"
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'middle_name', 'last_name',
            'registration_number', 'gender', 'course', 'department',
            'phone', 'email', 'year_of_study', 'onstation_supervisor',
            'oncampus_supervisor', 'password1', 'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help texts for better UI
        for field in ['username', 'password1', 'password2']:
            self.fields[field].help_text = ''

    def clean_registration_number(self):
        reg_no = self.cleaned_data.get('registration_number')
        if StudentProfile.objects.filter(registration_number=reg_no).exists():
            raise forms.ValidationError("This registration number is already in use.")
        return reg_no

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError("First name is required.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError("Surname is required.")
        return last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'

        # Assign only fields that exist on CustomUser
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data.get('email', '')

        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                registration_number=self.cleaned_data['registration_number'],
                gender=self.cleaned_data.get('gender', ''),
                course=self.cleaned_data.get('course'),
                department=self.cleaned_data.get('department'),
                phone_number=self.cleaned_data.get('phone', ''),
                year_of_study=self.cleaned_data.get('year_of_study'),
                supervisor_onstation=self.cleaned_data.get('onstation_supervisor'),
                supervisor_oncampus=self.cleaned_data.get('oncampus_supervisor'),
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
        # Remove default help texts
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''


# ==========================
# ON-STATION SUPERVISOR SIGN UP FORM
# ==========================

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)

class OnStationSupervisorSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Second Name")
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    company_name = forms.CharField(max_length=100, required=True, label="Company / Institution Name")
    position = forms.CharField(max_length=100, required=True, label="Your Position")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Enter New Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'gender', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default help texts
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']  # Assuming phone is a field on CustomUser
        user.gender = self.cleaned_data['gender']  # Assuming gender is a field on CustomUser
        user.role = 'onstation'

        if commit:
            user.save()
            OnStationSupervisor.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                position=self.cleaned_data['position'],
            )
        return user


# ==========================
# ON-CAMPUS SUPERVISOR SIGN UP FORM
# ==========================
from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser, SupervisorProfile
from users.models import Department  # Import your Department model

class OnCampusSupervisorSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    middle_name = forms.CharField(max_length=30, required=False, label="Second Name")
    last_name = forms.CharField(max_length=30, required=True, label="Surname")
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    position = forms.CharField(max_length=100, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'middle_name', 'last_name',
            'email', 'phone', 'department', 'position',
            'password1', 'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.middle_name = self.cleaned_data.get('middle_name', '')
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.role = 'oncampus'
        user.department = self.cleaned_data['department']  # ✅ assign the Department instance

        if commit:
            user.save()
            SupervisorProfile.objects.create(
                user=user,
                department=self.cleaned_data['department'].name,  # store just the name if it's CharField in profile
                phone=self.cleaned_data['phone'],
                position=self.cleaned_data['position'],
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


# ==========================
# STUDENT PROFILE FORM
# ==========================
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'registration_number',
            'course',
            'year_of_study',
            'phone_number',
            'profile_picture',
            'institution_name',
            'department',
            'gender',
            'date_of_birth',
            'address',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


# ==========================
# TASK ASSIGN FORM
# ==========================
class TaskAssignForm(forms.Form):
    task_description = forms.CharField(widget=forms.Textarea, label="Task Description")
    student_ids = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Assign to Students"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only students supervised by this user
            self.fields['student_ids'].queryset = StudentProfile.objects.filter(supervisor=user)

from django import forms
from .models import OnStationSupervisor

class OnStationSupervisorForm(forms.ModelForm):
    # Extra fields from User model
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = OnStationSupervisor
        fields = ['company_name', 'position']  # Only OnStationSupervisor model fields
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
        }

from django import forms

class RejectionForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Reason for rejection'}),
        required=False,
        label='Rejection Reason (optional)'
    )

from django import forms
from .models import StudentProfile

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_picture']
