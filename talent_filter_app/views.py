from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import RecruiterSignUpForm, JobSeekerSignUpForm, UserLoginForm
from .models import UserType

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

def recruiter_signup(request):
    if request.method == 'POST':
        form = RecruiterSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = RecruiterSignUpForm()
    return render(request, 'recruiter_signup.html', {'form': form})

def job_seeker_signup(request):
    if request.method == 'POST':
        form = JobSeekerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('job_seeker_dashboard')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = JobSeekerSignUpForm()
    return render(request, 'job_seeker_signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')

@login_required
def dashboard(request):
    # The @login_required decorator already ensures authentication

    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            # If user is not a recruiter, they must be a job seeker
            return redirect('job_seeker_dashboard')
    except UserType.DoesNotExist:
        # If no user type exists, create one based on the current view
        UserType.objects.create(user=request.user, is_recruiter=True, is_job_seeker=False)

    return render(request, 'dashboard.html')

@login_required
def job_listings(request):
    return render(request, 'job_listings.html')

@login_required
def candidate_management(request):
    return render(request, 'candidate_management.html')

@login_required
def ai_recommendations(request):
    return render(request, 'ai_recommendations.html')

@login_required
def shortlisted_candidates(request):
    return render(request, 'shortlisted_candidates.html')

@login_required
def reports_analytics(request):
    return render(request, 'reports_analytics.html')

@login_required
def settings(request):
    return render(request, 'settings.html')

@login_required
def job_seeker_dashboard(request):
    # The @login_required decorator already ensures authentication

    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            # If user is a recruiter, redirect to recruiter dashboard
            return redirect('dashboard')
    except UserType.DoesNotExist:
        # If no user type exists, create one as job seeker to prevent loops
        UserType.objects.create(user=request.user, is_job_seeker=True, is_recruiter=False)

    return render(request, 'job_seeker_dashboard.html')

@login_required
def available_jobs(request):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
        pass
    return render(request, 'available_jobs.html')

@login_required
def my_applications(request):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
        pass
    return render(request, 'my_applications.html')

@login_required
def job_seeker_profile(request):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
        pass
    return render(request, 'job_seeker_profile.html')
