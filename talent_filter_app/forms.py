from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import RecruiterProfile, JobSeekerProfile

class UserLoginForm(AuthenticationForm):
    """Custom login form with user type selection"""
    
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'input', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'input', 'placeholder': 'Password'})

class RecruiterSignUpForm(UserCreationForm):
    """Form for recruiter registration"""
    company_name = forms.CharField(max_length=200, required=True)
    company_website = forms.URLField(required=False)
    role = forms.CharField(max_length=100, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super(RecruiterSignUpForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'input'})
    
    def save(self, commit=True):
        user = super(RecruiterSignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create or update the user's profile
            recruiter_profile = RecruiterProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                company_website=self.cleaned_data['company_website'],
                role=self.cleaned_data['role']
            )
            
            # Set user type
            user_type = user.usertype
            user_type.is_recruiter = True
            user_type.save()
            
        return user

class JobSeekerSignUpForm(UserCreationForm):
    """Form for job seeker registration"""
    skills = forms.CharField(widget=forms.Textarea, required=False)
    experience_years = forms.FloatField(required=False, min_value=0)
    education = forms.CharField(widget=forms.Textarea, required=False)
    location = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super(JobSeekerSignUpForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'input'})
    
    def save(self, commit=True):
        user = super(JobSeekerSignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create or update the user's profile
            job_seeker_profile = JobSeekerProfile.objects.create(
                user=user,
                skills=self.cleaned_data['skills'],
                experience_years=self.cleaned_data['experience_years'],
                education=self.cleaned_data['education'],
                location=self.cleaned_data['location']
            )
            
            # Set user type
            user_type = user.usertype
            user_type.is_job_seeker = True
            user_type.save()
            
        return user
