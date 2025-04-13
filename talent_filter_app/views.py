from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from .forms import RecruiterSignUpForm, JobSeekerSignUpForm, UserLoginForm, JobForm
from .models import UserType, Job, Company, Location, Application, Candidate, Notification

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
        except UserType.DoesNotExist:
            pass

    return render(request, 'view_job.html', {
        'job': job,
        'applications': applications,
        'is_owner': is_owner
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

    # Pagination
    paginator = Paginator(jobs_list, 10)  # Show 10 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)

    context = {
        'jobs': jobs,
        'employment_types': employment_types,
        'workplace_types': workplace_types,
        'filters': request.GET,
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

    except Exception:
        applications_list = []

    # Pagination
    paginator = Paginator(applications_list, 10)  # Show 10 applications per page
    page = request.GET.get('page')
    applications = paginator.get_page(page)

    return render(request, 'my_applications.html', {'applications': applications})

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
    return render(request, 'job_seeker_profile.html')

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
