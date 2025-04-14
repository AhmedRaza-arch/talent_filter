from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from .forms import RecruiterSignUpForm, JobSeekerSignUpForm, UserLoginForm, JobForm, UserProfileForm, JobSeekerProfileForm, CustomPasswordChangeForm, RecruiterProfileForm
from .models import UserType, Job, Company, Location, Application, Candidate, Notification, JobSeekerProfile, RecruiterProfile

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

    # Get recruiter profile
    try:
        recruiter_profile = request.user.recruiterprofile

        # Get recent jobs posted by this recruiter
        recent_jobs = Job.objects.filter(recruiter=recruiter_profile).order_by('-posted_date')[:5]

        # Get total jobs count
        total_jobs = Job.objects.filter(recruiter=recruiter_profile).count()

        # Get pending applications
        pending_applications = Application.objects.filter(
            job__recruiter=recruiter_profile,
            status='Pending Review'
        ).select_related('candidate', 'job')

        # Get shortlisted candidates
        shortlisted_candidates = Application.objects.filter(
            job__recruiter=recruiter_profile,
            status='Shortlisted'
        ).select_related('candidate').count()

        # Get all applications for dashboard metrics
        all_applications = Application.objects.filter(
            job__recruiter=recruiter_profile
        ).select_related('candidate')

        # Count applications by status
        application_status_counts = {
            'Pending Review': 0,
            'Interview Scheduled': 0,
            'Shortlisted': 0,
            'Rejected': 0,
            'Hired': 0
        }

        for app in all_applications:
            if app.status in application_status_counts:
                application_status_counts[app.status] += 1

        # For AI recommendations, we'll just use a placeholder count for now
        ai_recommendations_count = 15  # This would be replaced with actual AI logic in a real app

    except Exception as e:
        # If there's any error or the recruiter profile doesn't exist
        recent_jobs = []
        total_jobs = 0
        pending_applications = []
        shortlisted_candidates = 0
        application_status_counts = {
            'Pending Review': 0,
            'Interview Scheduled': 0,
            'Shortlisted': 0,
            'Rejected': 0,
            'Hired': 0
        }
        ai_recommendations_count = 0

    context = {
        'recent_jobs': recent_jobs,
        'total_jobs': total_jobs,
        'pending_applications': pending_applications,
        'pending_count': application_status_counts['Pending Review'],
        'shortlisted_count': shortlisted_candidates,
        'ai_recommendations_count': ai_recommendations_count,
        'application_status_counts': application_status_counts
    }

    return render(request, 'dashboard.html', context)

@login_required
def job_listings(request):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return redirect('job_seeker_dashboard')
    except UserType.DoesNotExist:
        return redirect('dashboard')

    # Get all jobs for the recruiter
    try:
        recruiter_profile = request.user.recruiterprofile
        # Filter jobs by recruiter profile
        jobs = Job.objects.filter(recruiter=recruiter_profile).order_by('-posted_date')
    except:
        jobs = []

    return render(request, 'job_listings.html', {'jobs': jobs})

@login_required
def candidate_management(request):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return redirect('job_seeker_dashboard')
    except UserType.DoesNotExist:
        return redirect('dashboard')

    # Get recruiter profile
    try:
        recruiter_profile = request.user.recruiterprofile

        # Get all applications for this recruiter's jobs (unfiltered for counts)
        all_applications = Application.objects.filter(
            job__recruiter=recruiter_profile
        ).select_related('candidate', 'job')

        # Calculate status counts from the unfiltered list
        status_counts = {
            'All': all_applications.count(),
            'Pending_Review': all_applications.filter(status='Pending Review').count(),
            'Interview_Scheduled': all_applications.filter(status='Interview Scheduled').count(),
            'Shortlisted': all_applications.filter(status='Shortlisted').count(),
            'Rejected': all_applications.filter(status='Rejected').count(),
            'Hired': all_applications.filter(status='Hired').count()
        }

        # Create a filtered list for display
        applications_list = all_applications

        # Filter by status if provided
        status_filter = request.GET.get('status', '')
        if status_filter:
            applications_list = applications_list.filter(status=status_filter)

        # Filter by job if provided
        job_filter = request.GET.get('job', '')
        if job_filter:
            applications_list = applications_list.filter(job__id=job_filter)

        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            applications_list = applications_list.filter(
                candidate__name__icontains=search_query
            )

        # Order by applied date (most recent first)
        applications_list = applications_list.order_by('-applied_date')

        # Get all jobs for this recruiter for the job filter dropdown
        jobs = Job.objects.filter(recruiter=recruiter_profile).order_by('-posted_date')

    except Exception as e:
        applications_list = []
        jobs = []
        status_counts = {
            'All': 0,
            'Pending_Review': 0,
            'Interview_Scheduled': 0,
            'Shortlisted': 0,
            'Rejected': 0,
            'Hired': 0
        }

    # Pagination
    paginator = Paginator(applications_list, 10)  # Show 10 applications per page
    page = request.GET.get('page')
    applications = paginator.get_page(page)

    # Get the current active filter for highlighting the tab
    current_filter = request.GET.get('status', 'All')
    current_job = request.GET.get('job', '')

    context = {
        'applications': applications,
        'jobs': jobs,
        'current_filter': current_filter,
        'current_job': current_job,
        'search_query': search_query if 'search_query' in locals() else '',
        'status_counts': status_counts
    }

    return render(request, 'candidate_management.html', context)

@login_required
def ai_recommendations(request):
    return render(request, 'ai_recommendations.html')

@login_required
def shortlisted_candidates(request):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return redirect('job_seeker_dashboard')
    except UserType.DoesNotExist:
        return redirect('dashboard')

    # Get recruiter profile
    try:
        recruiter_profile = request.user.recruiterprofile

        # Get all shortlisted applications for this recruiter's jobs
        applications_list = Application.objects.filter(
            job__recruiter=recruiter_profile,
            status='Shortlisted'
        ).select_related('candidate', 'job')

        # Filter by job if provided
        job_filter = request.GET.get('job', '')
        if job_filter:
            applications_list = applications_list.filter(job__id=job_filter)

        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            applications_list = applications_list.filter(
                candidate__name__icontains=search_query
            )

        # Order by skill match (highest first) and then by applied date (most recent first)
        applications_list = applications_list.order_by('-candidate__skill_match', '-applied_date')

        # Get all jobs for this recruiter for the job filter dropdown
        jobs = Job.objects.filter(recruiter=recruiter_profile).order_by('-posted_date')

        # Get shortlisted candidates count by job
        job_counts = {}
        for job in jobs:
            count = Application.objects.filter(
                job=job,
                status='Shortlisted'
            ).count()
            job_counts[job.id] = count

    except Exception as e:
        applications_list = []
        jobs = []
        job_counts = {}

    # Pagination
    paginator = Paginator(applications_list, 10)  # Show 10 applications per page
    page = request.GET.get('page')
    applications = paginator.get_page(page)

    # Get the current active job filter
    current_job = request.GET.get('job', '')

    # Get selected candidates for comparison
    selected_candidates = request.GET.getlist('compare', [])
    selected_applications = []

    if selected_candidates:
        selected_applications = Application.objects.filter(
            id__in=selected_candidates,
            job__recruiter=recruiter_profile,
            status='Shortlisted'
        ).select_related('candidate', 'job')

    context = {
        'applications': applications,
        'jobs': jobs,
        'job_counts': job_counts,
        'current_job': current_job,
        'search_query': search_query if 'search_query' in locals() else '',
        'selected_applications': selected_applications,
        'total_shortlisted': applications_list.count() if 'applications_list' in locals() else 0
    }

    return render(request, 'shortlisted_candidates.html', context)

@login_required
def reports_analytics(request):
    return render(request, 'reports_analytics.html')

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

    # Initialize forms
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'user_profile':
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Personal information updated successfully!")
                return redirect('settings')

        elif form_type == 'recruiter_profile':
            profile_form = RecruiterProfileForm(request.POST, request.FILES, instance=recruiter_profile)
            if profile_form.is_valid():
                profile = profile_form.save(commit=False)

                # Handle profile picture upload
                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']

                profile.save()
                messages.success(request, "Professional information updated successfully!")
                return redirect('settings')

        elif form_type == 'password_change':
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Password changed successfully!")
                return redirect('settings')

        # If we get here, there was an error in the form submission
        # We'll recreate the appropriate form with errors below
    else:
        # Initialize all forms with current data
        user_form = UserProfileForm(instance=request.user)
        profile_form = RecruiterProfileForm(instance=recruiter_profile)
        password_form = CustomPasswordChangeForm(request.user)

    # If we're handling a POST request with errors, initialize the non-submitted forms
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'user_profile':
            profile_form = RecruiterProfileForm(instance=recruiter_profile)
            password_form = CustomPasswordChangeForm(request.user)
        elif form_type == 'recruiter_profile':
            user_form = UserProfileForm(instance=request.user)
            password_form = CustomPasswordChangeForm(request.user)
        elif form_type == 'password_change':
            user_form = UserProfileForm(instance=request.user)
            profile_form = RecruiterProfileForm(instance=recruiter_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'recruiter_profile': recruiter_profile,
    }

    return render(request, 'settings.html', context)

@login_required
def add_job(request):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return redirect('job_seeker_dashboard')
    except UserType.DoesNotExist:
        return redirect('dashboard')

    if request.method == 'POST':
        form = JobForm(request.POST, user=request.user)
        if form.is_valid():
            job = form.save()
            messages.success(request, f"Job '{job.job_title}' has been created successfully!")
            return redirect('job_listings')
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        form = JobForm(user=request.user)

    return render(request, 'add_job.html', {'form': form})

@login_required
def edit_job(request, job_id):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return redirect('job_seeker_dashboard')
    except UserType.DoesNotExist:
        return redirect('dashboard')

    job = get_object_or_404(Job, id=job_id)

    # Check if the job belongs to the recruiter
    try:
        recruiter_profile = request.user.recruiterprofile
        if job.recruiter != recruiter_profile:
            messages.error(request, "You don't have permission to edit this job.")
            return redirect('job_listings')
    except:
        messages.error(request, "You don't have permission to edit this job.")
        return redirect('job_listings')

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job, user=request.user)
        if form.is_valid():
            job = form.save()
            messages.success(request, f"Job '{job.job_title}' has been updated successfully!")
            return redirect('job_listings')
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        # Prepare initial data for the form
        initial_data = {
            'company_name': job.company.name,
            'city': job.company.location.city,
            'state': job.company.location.state,
            'country': job.company.location.country,
            'key_responsibilities': '\n'.join(job.get_key_responsibilities()),
            'requirements': '\n'.join(job.get_requirements()),
            'skills_required': '\n'.join(job.get_skills_required()),
        }

        if job.nice_to_have:
            initial_data['nice_to_have'] = '\n'.join(job.get_nice_to_have())

        if job.external_portals:
            initial_data['external_portals'] = '\n'.join(job.get_external_portals())

        form = JobForm(instance=job, initial=initial_data, user=request.user)

    return render(request, 'add_job.html', {'form': form, 'job': job, 'is_edit': True})

@login_required
def view_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Get applications for this job if the user is a recruiter and owns the job
    applications = []
    is_owner = False
    has_applied = False

    if request.user.is_authenticated:
        try:
            user_type = UserType.objects.get(user=request.user)
            if user_type.is_recruiter:
                try:
                    recruiter_profile = request.user.recruiterprofile
                    if job.recruiter == recruiter_profile:
                        is_owner = True
                        applications = Application.objects.filter(job=job).select_related('candidate')
                except:
                    pass
            elif user_type.is_job_seeker:
                # Check if the job seeker has already applied to this job
                try:
                    candidates = Candidate.objects.filter(
                        name=request.user.get_full_name() or request.user.username
                    )
                    if candidates.exists():
                        has_applied = Application.objects.filter(
                            job=job,
                            candidate__in=candidates
                        ).exists()
                except Exception:
                    pass
        except UserType.DoesNotExist:
            pass

    return render(request, 'view_job.html', {
        'job': job,
        'applications': applications,
        'is_owner': is_owner,
        'has_applied': has_applied
    })

@login_required
def delete_job(request, job_id):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return redirect('job_seeker_dashboard')
    except UserType.DoesNotExist:
        return redirect('dashboard')

    job = get_object_or_404(Job, id=job_id)

    # Check if the job belongs to the recruiter
    try:
        recruiter_profile = request.user.recruiterprofile
        if job.recruiter != recruiter_profile:
            messages.error(request, "You don't have permission to delete this job.")
            return redirect('job_listings')
    except:
        messages.error(request, "You don't have permission to delete this job.")
        return redirect('job_listings')

    if request.method == 'POST':
        job_title = job.job_title
        job.delete()
        messages.success(request, f"Job '{job_title}' has been deleted successfully!")
        return redirect('job_listings')

    return render(request, 'delete_job_confirm.html', {'job': job})

@login_required
def update_job_status(request, job_id):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return JsonResponse({'status': 'error', 'message': 'Only recruiters can update job status'})
    except UserType.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User type not found'})

    job = get_object_or_404(Job, id=job_id)

    # Check if the job belongs to the recruiter
    try:
        recruiter_profile = request.user.recruiterprofile
        if job.recruiter != recruiter_profile:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to update this job'})
    except:
        return JsonResponse({'status': 'error', 'message': 'Recruiter profile not found'})

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Job._meta.get_field('status').choices):
            job.status = new_status
            job.save()
            return JsonResponse({'status': 'success', 'message': f'Job status updated to {new_status}'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid status value'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def update_application_status(request, application_id):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return JsonResponse({'status': 'error', 'message': 'Only recruiters can update application status'})
    except UserType.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User type not found'})

    application = get_object_or_404(Application, id=application_id)

    # Check if the job belongs to the recruiter
    try:
        recruiter_profile = request.user.recruiterprofile
        if application.job.recruiter != recruiter_profile:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to update this application'})
    except:
        return JsonResponse({'status': 'error', 'message': 'Recruiter profile not found'})

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application._meta.get_field('status').choices):
            old_status = application.status
            application.status = new_status
            application.save()

            # Create notification for the job seeker
            # Find the candidate's user
            try:
                # We need to find the user associated with this candidate
                # This is a simplified approach - in a real app, you'd have a direct link
                job_seekers = User.objects.filter(jobseekerprofile__isnull=False)
                for job_seeker in job_seekers:
                    if job_seeker.get_full_name() == application.candidate.name or job_seeker.username == application.candidate.name:
                        # Create notification with appropriate message based on status
                        message = f"Your application for {application.job.job_title} has been updated to '{new_status}'."

                        # Add more specific messages for different statuses
                        if new_status == 'Interview Scheduled':
                            message = f"Good news! You've been selected for an interview for the {application.job.job_title} position at {application.job.company.name}."
                        elif new_status == 'Shortlisted':
                            message = f"Congratulations! You've been shortlisted for the {application.job.job_title} position at {application.job.company.name}."
                        elif new_status == 'Rejected':
                            message = f"Thank you for your interest in the {application.job.job_title} position at {application.job.company.name}. Unfortunately, we've decided to move forward with other candidates."
                        elif new_status == 'Hired':
                            message = f"Congratulations! You've been selected for the {application.job.job_title} position at {application.job.company.name}."

                        create_notification(
                            recipient=job_seeker,
                            message=message,
                            notification_type='application',
                            sender=request.user,
                            related_link=reverse('my_applications')
                        )
                        break
            except Exception as e:
                # Log the error but don't stop the status update
                print(f"Error creating notification: {str(e)}")

            return JsonResponse({'status': 'success', 'message': f'Application status updated to {new_status}'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid status value'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

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

    # Get available jobs count
    available_jobs_count = Job.objects.filter(status='Open').count()

    # Get user's applications
    user_applications = []
    applications_count = 0

    try:
        # Get or retrieve candidate record for this job seeker
        candidates = Candidate.objects.filter(
            name=request.user.get_full_name() or request.user.username
        )

        # Get applications for these candidates
        if candidates.exists():
            user_applications = Application.objects.filter(candidate__in=candidates)\
                .select_related('job', 'job__company')\
                .order_by('-applied_date')[:5]  # Get 5 most recent applications

            applications_count = Application.objects.filter(candidate__in=candidates).count()
    except Exception as e:
        print(f"Error fetching applications: {str(e)}")

    # Calculate profile completion percentage
    profile_completion = 0
    try:
        job_seeker_profile = request.user.jobseekerprofile

        # Count completed profile fields
        completed_fields = 0
        total_fields = 5  # Total number of important profile fields

        if job_seeker_profile.profile_picture:
            completed_fields += 1
        if job_seeker_profile.resume:
            completed_fields += 1
        if job_seeker_profile.skills:
            completed_fields += 1
        if job_seeker_profile.experience_years > 0:
            completed_fields += 1
        if job_seeker_profile.location:
            completed_fields += 1

        profile_completion = int((completed_fields / total_fields) * 100)
    except Exception as e:
        print(f"Error calculating profile completion: {str(e)}")

    # Get recent job listings
    recent_jobs = Job.objects.filter(status='Open').select_related('company', 'company__location')\
        .order_by('-posted_date')[:5]  # Get 5 most recent jobs

    # Create a set of job IDs that the user has already applied for
    applied_job_ids = set()

    # Get candidate record for this job seeker if not already retrieved
    if 'candidates' not in locals():
        try:
            candidates = Candidate.objects.filter(
                name=request.user.get_full_name() or request.user.username
            )
        except Exception:
            candidates = Candidate.objects.none()

    # Check if candidates exist
    if candidates.exists():
        # Get all jobs the user has applied for
        applied_job_ids = set(Application.objects.filter(candidate__in=candidates)\
            .values_list('job_id', flat=True))

    context = {
        'available_jobs_count': available_jobs_count,
        'applications_count': applications_count,
        'profile_completion': profile_completion,
        'recent_jobs': recent_jobs,
        'recent_applications': user_applications,
        'applied_job_ids': applied_job_ids,
    }

    return render(request, 'job_seeker_dashboard.html', context)

@login_required
def available_jobs(request):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
        pass

    # Get all open jobs
    jobs_list = Job.objects.filter(status='Open').order_by('-posted_date')

    # Apply filters if provided
    if request.GET:
        # Filter by department/job title (search term)
        search_term = request.GET.get('search', '')
        if search_term:
            jobs_list = jobs_list.filter(job_title__icontains=search_term)

        # Filter by experience level
        experience = request.GET.get('experience', '')
        if experience:
            jobs_list = jobs_list.filter(experience_required__icontains=experience)

        # Filter by location
        location = request.GET.get('location', '')
        if location:
            jobs_list = jobs_list.filter(company__location__city__icontains=location) | \
                  jobs_list.filter(company__location__state__icontains=location) | \
                  jobs_list.filter(company__location__country__icontains=location)

        # Filter by employment type
        employment_type = request.GET.get('employment_type', '')
        if employment_type:
            jobs_list = jobs_list.filter(employment_type=employment_type)

        # Filter by workplace type
        workplace_type = request.GET.get('workplace_type', '')
        if workplace_type:
            jobs_list = jobs_list.filter(workplace_type=workplace_type)

    # Get unique values for filters
    employment_types = Job.objects.values_list('employment_type', flat=True).distinct()
    workplace_types = Job.objects.values_list('workplace_type', flat=True).distinct()

    # Get candidate record for this job seeker
    applied_job_ids = set()
    try:
        candidates = Candidate.objects.filter(
            name=request.user.get_full_name() or request.user.username
        )

        # Get all jobs the user has applied for
        if candidates.exists():
            applied_job_ids = set(Application.objects.filter(candidate__in=candidates)\
                .values_list('job_id', flat=True))
    except Exception:
        pass

    # Pagination
    paginator = Paginator(jobs_list, 10)  # Show 10 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'employment_types': employment_types,
        'workplace_types': workplace_types,
        'filters': request.GET,
        'applied_job_ids': applied_job_ids,
    }

    return render(request, 'available_jobs.html', context)

@login_required
def apply_to_job(request, job_id):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
        return redirect('dashboard')

    # Get the job
    job = get_object_or_404(Job, id=job_id)

    # Check if the job is open
    if job.status != 'Open':
        messages.error(request, "This job is no longer accepting applications.")
        return redirect('view_job', job_id=job_id)

    # Check if the user already applied to this job
    try:
        job_seeker_profile = request.user.jobseekerprofile

        # Get or create a candidate record for this job seeker
        candidate, created = Candidate.objects.get_or_create(
            name=request.user.get_full_name() or request.user.username,
            defaults={
                'role': job_seeker_profile.user.username,
                'skill_match': 75,  # Default value, could be calculated based on job requirements
                'experience': job_seeker_profile.experience_years,
                'location': job_seeker_profile.location or 'Not specified',
                'photo': job_seeker_profile.profile_picture,
                'resume': job_seeker_profile.resume
            }
        )

        # Check if already applied
        existing_application = Application.objects.filter(job=job, candidate=candidate).exists()
        if existing_application:
            messages.info(request, "You have already applied to this job.")
            return redirect('my_applications')

        # Create the application
        application = Application.objects.create(
            job=job,
            candidate=candidate,
            status='Pending Review'
        )

        # Create notification for the recruiter
        create_notification(
            recipient=job.recruiter.user,
            message=f"New application received for {job.job_title} from {candidate.name}",
            notification_type='application',
            sender=request.user,
            related_link=reverse('view_job', args=[job.id])
        )

        messages.success(request, f"You have successfully applied to {job.job_title} at {job.company.name}.")
        return redirect('my_applications')

    except Exception as e:
        messages.error(request, f"There was an error processing your application: {str(e)}")
        return redirect('view_job', job_id=job_id)

@login_required
def my_applications(request):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
        pass

    # Get the job seeker's applications
    try:
        job_seeker_profile = request.user.jobseekerprofile

        # Get or retrieve candidate record for this job seeker
        candidates = Candidate.objects.filter(
            name=request.user.get_full_name() or request.user.username
        )

        # Get applications for these candidates
        applications_list = Application.objects.filter(candidate__in=candidates).select_related('job', 'job__company').order_by('-applied_date')

        # Filter by status if provided
        status_filter = request.GET.get('status', '')
        if status_filter:
            applications_list = applications_list.filter(status=status_filter)

    except Exception:
        applications_list = []

    # Pagination
    paginator = Paginator(applications_list, 10)  # Show 10 applications per page
    page = request.GET.get('page')
    applications = paginator.get_page(page)

    # Get the current active filter for highlighting the tab
    current_filter = request.GET.get('status', 'All')

    return render(request, 'my_applications.html', {
        'applications': applications,
        'current_filter': current_filter
    })

@login_required
def withdraw_application(request, application_id):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
        return redirect('dashboard')

    # Get the application
    application = get_object_or_404(Application, id=application_id)

    # Verify that the application belongs to the user
    try:
        candidates = Candidate.objects.filter(
            name=request.user.get_full_name() or request.user.username
        )

        if application.candidate not in candidates:
            messages.error(request, "You don't have permission to withdraw this application.")
            return redirect('my_applications')

        # Delete the application
        job_title = application.job.job_title
        application.delete()

        messages.success(request, f"Your application for {job_title} has been withdrawn.")
        return redirect('my_applications')

    except Exception as e:
        messages.error(request, f"There was an error withdrawing your application: {str(e)}")
        return redirect('my_applications')

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

    # Calculate profile completion percentage
    profile_completion = calculate_profile_completion(request.user, job_seeker_profile)

    # Print debug information
    if job_seeker_profile.profile_picture:
        print(f"Profile picture URL: {job_seeker_profile.profile_picture.url}")

    # Initialize forms
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'user_profile':
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Personal information updated successfully!")
                return redirect('job_seeker_profile')

        elif form_type == 'job_seeker_profile':
            profile_form = JobSeekerProfileForm(request.POST, request.FILES, instance=job_seeker_profile)
            if profile_form.is_valid():
                profile = profile_form.save(commit=False)

                # Handle profile picture upload
                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']
                    print(f"Uploaded profile picture: {profile.profile_picture.name}")

                # Handle resume upload
                if 'resume' in request.FILES:
                    profile.resume = request.FILES['resume']
                    print(f"Uploaded resume: {profile.resume.name}")

                profile.save()
                messages.success(request, "Professional information updated successfully!")
                return redirect('job_seeker_profile')

        elif form_type == 'password_change':
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Password changed successfully!")
                return redirect('job_seeker_profile')

        # If we get here, there was an error in the form submission
        # We'll recreate the appropriate form with errors below
    else:
        # Initialize all forms with current data
        user_form = UserProfileForm(instance=request.user)
        profile_form = JobSeekerProfileForm(instance=job_seeker_profile)
        password_form = CustomPasswordChangeForm(request.user)

    # If we're handling a POST request with errors, initialize the non-submitted forms
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'user_profile':
            profile_form = JobSeekerProfileForm(instance=job_seeker_profile)
            password_form = CustomPasswordChangeForm(request.user)
        elif form_type == 'job_seeker_profile':
            user_form = UserProfileForm(instance=request.user)
            password_form = CustomPasswordChangeForm(request.user)
        elif form_type == 'password_change':
            user_form = UserProfileForm(instance=request.user)
            profile_form = JobSeekerProfileForm(instance=job_seeker_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'profile_completion': profile_completion,
        'job_seeker_profile': job_seeker_profile,
    }

    return render(request, 'job_seeker_profile.html', context)

# Helper function to calculate profile completion
def calculate_profile_completion(user, profile):
    """Calculate the profile completion percentage"""
    completed_fields = 0
    total_fields = 8  # Total number of important profile fields

    # User model fields
    if user.first_name:
        completed_fields += 1
    if user.last_name:
        completed_fields += 1
    if user.email:
        completed_fields += 1

    # JobSeekerProfile fields
    if profile.profile_picture:
        completed_fields += 1
    if profile.resume:
        completed_fields += 1
    if profile.skills:
        completed_fields += 1
    if profile.experience_years > 0:
        completed_fields += 1
    if profile.location:
        completed_fields += 1

    return int((completed_fields / total_fields) * 100)

@login_required
def notifications_list(request):
    """View to display all notifications for the current user"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    # Pagination
    paginator = Paginator(notifications, 10)  # Show 10 notifications per page
    page = request.GET.get('page')
    notifications_page = paginator.get_page(page)

    return render(request, 'notifications.html', {'notifications': notifications_page})

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read and redirect to its related link"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    # Mark as read
    notification.is_read = True
    notification.save()

    # Redirect to related link if available, otherwise to notifications list
    if notification.related_link:
        return redirect(notification.related_link)
    else:
        return redirect('notifications_list')

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications_list')

@login_required
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    messages.success(request, "Notification deleted.")
    return redirect('notifications_list')

# Helper function to create notifications
def create_notification(recipient, message, notification_type, sender=None, related_link=None):
    """Create a new notification"""
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        message=message,
        notification_type=notification_type,
        related_link=related_link
    )
    return notification
