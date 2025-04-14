from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import RecruiterProfile, JobSeekerProfile, Job, Company, Location
import json

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

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['city', 'state', 'country']

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'input'})

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'input'})

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class JobSeekerProfileForm(forms.ModelForm):
    """Form for updating job seeker profile information"""

    class Meta:
        model = JobSeekerProfile
        fields = ['profile_picture', 'resume', 'skills', 'experience_years', 'education', 'location']
        widgets = {
            'skills': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Enter your skills (e.g., Python, JavaScript, Project Management)'}),
            'education': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Enter your education details'}),
            'location': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Enter your location'}),
            'experience_years': forms.NumberInput(attrs={'class': 'input', 'min': '0', 'step': '0.5'}),
        }

class RecruiterProfileForm(forms.ModelForm):
    """Form for updating recruiter profile information"""

    class Meta:
        model = RecruiterProfile
        fields = ['profile_picture', 'role', 'company_name', 'company_website']
        widgets = {
            'role': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Enter your role (e.g., HR Manager, Talent Acquisition Specialist)'}),
            'company_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Enter your company name'}),
            'company_website': forms.URLInput(attrs={'class': 'input', 'placeholder': 'Enter your company website URL'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styling"""

    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class JobForm(forms.ModelForm):
    # Company and location fields
    company_name = forms.CharField(max_length=200, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    country = forms.CharField(max_length=100, required=True)

    # Array fields that will be stored as JSON
    key_responsibilities = forms.CharField(widget=forms.Textarea, required=True,
                                         help_text="Enter each responsibility on a new line")
    requirements = forms.CharField(widget=forms.Textarea, required=True,
                                help_text="Enter each requirement on a new line")
    nice_to_have = forms.CharField(widget=forms.Textarea, required=False,
                                help_text="Enter each nice-to-have on a new line")
    skills_required = forms.CharField(widget=forms.Textarea, required=True,
                                    help_text="Enter each skill on a new line")
    external_portals = forms.CharField(widget=forms.Textarea, required=False,
                                     help_text="Enter each portal on a new line")

    # Application deadline
    application_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = Job
        fields = [
            'job_title', 'workplace_type', 'employment_type', 'experience_required',
            'summary', 'recruiter_name', 'recruiter_position', 'recruiter_email',
            'recruiter_linkedin', 'application_link', 'how_to_apply', 'open_positions'
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
            'how_to_apply': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(JobForm, self).__init__(*args, **kwargs)

        # Set default values from RecruiterProfile if available
        if self.user and hasattr(self.user, 'recruiterprofile'):
            profile = self.user.recruiterprofile
            self.fields['recruiter_name'].initial = self.user.get_full_name() or self.user.username
            self.fields['recruiter_position'].initial = profile.role
            self.fields['company_name'].initial = profile.company_name

        # Add Bulma classes to all fields
        for field_name in self.fields:
            field = self.fields[field_name]
            css_class = 'input'
            if isinstance(field.widget, forms.Textarea):
                css_class = 'textarea'
            elif isinstance(field.widget, forms.Select):
                css_class = 'select is-fullwidth'
                field.widget.attrs.update({'class': ''})
                continue
            field.widget.attrs.update({'class': css_class})

    def clean(self):
        cleaned_data = super().clean()

        # Convert textarea inputs to lists for JSON fields
        for field_name in ['key_responsibilities', 'requirements', 'nice_to_have', 'skills_required', 'external_portals']:
            if field_name in cleaned_data and cleaned_data[field_name]:
                # Split by newline and remove empty lines
                items = [item.strip() for item in cleaned_data[field_name].split('\n') if item.strip()]
                cleaned_data[field_name] = items

        return cleaned_data

    def save(self, commit=True):
        job = super(JobForm, self).save(commit=False)

        # Create or get location
        location, _ = Location.objects.get_or_create(
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            country=self.cleaned_data['country']
        )

        # Create or get company
        company, _ = Company.objects.get_or_create(
            name=self.cleaned_data['company_name'],
            defaults={'location': location}
        )

        # Set company for the job
        job.company = company

        # Set recruiter information
        if self.user and hasattr(self.user, 'recruiterprofile'):
            job.recruiter = self.user.recruiterprofile

        # Set JSON fields
        job.set_key_responsibilities(self.cleaned_data['key_responsibilities'])
        job.set_requirements(self.cleaned_data['requirements'])
        if 'nice_to_have' in self.cleaned_data and self.cleaned_data['nice_to_have']:
            job.set_nice_to_have(self.cleaned_data['nice_to_have'])
        job.set_skills_required(self.cleaned_data['skills_required'])
        if 'external_portals' in self.cleaned_data and self.cleaned_data['external_portals']:
            job.set_external_portals(self.cleaned_data['external_portals'])

        if commit:
            job.save()

        return job
