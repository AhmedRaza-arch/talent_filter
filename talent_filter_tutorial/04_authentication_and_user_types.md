# 4. Authentication and User Types

## Managing Different User Roles

In this section, we'll explore how Talent Filter handles authentication and manages different user types (job seekers and recruiters). This dual-user system is a fundamental aspect of the application's architecture.

## Authentication Overview

Talent Filter uses Django's built-in authentication system with custom extensions to support different user types. The key components are:

1. **Django's User Model**: Handles core authentication (username, password, etc.)
2. **UserType Model**: Extends User to specify if a user is a job seeker or recruiter
3. **Profile Models**: Store additional information for each user type (RecruiterProfile, JobSeekerProfile)
4. **Custom Forms**: Handle registration and login for different user types
5. **View Decorators**: Ensure users can only access appropriate views

## User Registration Flow

Let's examine how users register in the system:

### Job Seeker Registration

```python
def job_seeker_signup(request):
    if request.method == 'POST':
        form = JobSeekerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Please complete your profile to continue.")
            return redirect('job_seeker_profile')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = JobSeekerSignUpForm()
    return render(request, 'job_seeker_signup.html', {'form': form})
```

The `JobSeekerSignUpForm` handles the creation of both the User and UserType records:

```python
class JobSeekerSignUpForm(UserCreationForm):
    """Form for job seeker registration"""
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super(JobSeekerSignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create a minimal profile - details will be filled in later
            job_seeker_profile = JobSeekerProfile.objects.create(
                user=user
            )
            
            # Set user type
            user_type = user.usertype
            user_type.is_job_seeker = True
            user_type.save()
        
        return user
```

### Recruiter Registration

The recruiter registration process is similar but sets different flags:

```python
def recruiter_signup(request):
    if request.method == 'POST':
        form = RecruiterSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Please complete your profile to continue.")
            return redirect('settings')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = RecruiterSignUpForm()
    return render(request, 'recruiter_signup.html', {'form': form})
```

The `RecruiterSignUpForm` creates a RecruiterProfile and sets the appropriate UserType flags:

```python
class RecruiterSignUpForm(UserCreationForm):
    """Form for recruiter registration"""
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super(RecruiterSignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create a minimal profile - details will be filled in later in settings
            recruiter_profile = RecruiterProfile.objects.create(
                user=user,
                role="" # Empty role that will be filled in settings
            )
            
            # Set user type
            user_type = user.usertype
            user_type.is_recruiter = True
            user_type.save()
        
        return user
```

## Login and Redirection

The login view authenticates users and redirects them to the appropriate dashboard based on their user type:

```python
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user type
                try:
                    user_type = UserType.objects.get(user=user)
                    if user_type.is_job_seeker:
                        return redirect('job_seeker_dashboard')
                    elif user_type.is_recruiter:
                        return redirect('dashboard')
                except UserType.DoesNotExist:
                    # Default to dashboard if no user type is set
                    return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})
```

## Protecting Views by User Type

Views are protected to ensure users can only access appropriate pages. This is done by checking the user type at the beginning of view functions:

### Recruiter-Only Views

```python
@login_required
def dashboard(request):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            # If user is not a recruiter, they must be a job seeker
            return redirect('job_seeker_dashboard')
    except UserType.DoesNotExist:
        # If no user type exists, create one based on the current view
        UserType.objects.create(user=request.user, is_recruiter=True, is_job_seeker=False)
    
    # Recruiter-specific code...
```

### Job Seeker-Only Views

```python
@login_required
def job_seeker_dashboard(request):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            # If user is a recruiter, redirect to recruiter dashboard
            return redirect('dashboard')
    except UserType.DoesNotExist:
        # If no user type exists, create one as job seeker to prevent loops
        UserType.objects.create(user=request.user, is_job_seeker=True, is_recruiter=False)
    
    # Job seeker-specific code...
```

## User Profiles

After registration, users are directed to complete their profiles:

### Job Seeker Profile

Job seekers can upload a resume, profile picture, and provide additional information:

```python
@login_required
def job_seeker_profile(request):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
        pass
    
    # Get or create job seeker profile
    job_seeker_profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    
    # Handle form submission...
```

### Recruiter Profile

Recruiters provide information about their role and company:

```python
@login_required
def settings(request):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return redirect('job_seeker_profile')
    except UserType.DoesNotExist:
        return redirect('dashboard')
    
    # Get or create recruiter profile
    recruiter_profile, created = RecruiterProfile.objects.get_or_create(user=request.user)
    
    # Handle form submission...
```

## Authentication Templates

The application includes several templates for authentication:

- `login.html`: Shared login form
- `recruiter_signup.html`: Recruiter registration form
- `job_seeker_signup.html`: Job seeker registration form

These templates use Django's form handling and display appropriate error messages.

## Password Management

The application includes functionality for changing passwords:

```python
class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styling"""
    
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
```

This form is used in both the job seeker profile and recruiter settings pages.

## Logout

The logout view is straightforward:

```python
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')
```

## Context Processors

The application uses a context processor to add notification information to all templates:

```python
# context_processors.py
def notifications(request):
    """Add unread notification count to context"""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        recent_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')[:5]
        
        return {
            'unread_notification_count': unread_count,
            'recent_notifications': recent_notifications
        }
    return {'unread_notification_count': 0, 'recent_notifications': []}
```

This is registered in `settings.py`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ...
                'talent_filter_app.context_processors.notifications',
            ],
        },
    },
]
```

## Try It Yourself: Authentication Flow

Let's practice tracing the authentication flow:

1. Find the URL patterns for login, signup, and logout in `urls.py`
2. Examine how the login form is rendered in `login.html`
3. Trace what happens when a job seeker registers and logs in
4. Identify how the application prevents a job seeker from accessing recruiter views

## Security Considerations

When working with authentication, keep these security considerations in mind:

1. **Password Storage**: Django securely hashes passwords by default
2. **CSRF Protection**: Django includes CSRF protection for forms
3. **Session Security**: Use HTTPS in production to protect session cookies
4. **Permission Checks**: Always verify user permissions in view functions
5. **Secure Redirects**: Be careful with redirects after authentication

## Next Steps

In the next section, we'll explore the recruiter features of the application, including job posting, candidate management, and AI recommendations.
