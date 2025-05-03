# 5. Recruiter Features

## Understanding the Recruiter Experience

In this section, we'll explore the features available to recruiters in the Talent Filter application. Recruiters can post jobs, manage applications, and use AI to find suitable candidates.

## Recruiter Dashboard

The recruiter dashboard provides an overview of activity and quick access to key features:

```python
@login_required
def dashboard(request):
    # Check if user is a recruiter
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_recruiter:
            return redirect('job_seeker_dashboard')
    except UserType.DoesNotExist:
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

        # Count applications by status
        application_status_counts = {
            'Pending Review': 0,
            'Interview Scheduled': 0,
            'Shortlisted': 0,
            'Rejected': 0,
            'Hired': 0
        }

        all_applications = Application.objects.filter(
            job__recruiter=recruiter_profile
        ).select_related('candidate')

        for app in all_applications:
            if app.status in application_status_counts:
                application_status_counts[app.status] += 1

        # Get count of potential AI recommendations
        ai_recommendations_count = JobSeekerProfile.objects.filter(
            skills__isnull=False  # Must have skills
        ).count()

    except Exception as e:
        # Handle errors
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
```

The dashboard template (`dashboard.html`) displays:
- Recent job postings
- Application statistics
- Quick links to manage candidates
- Notifications

## Job Management

Recruiters can create, edit, view, and delete job postings:

### Creating a Job

```python
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
```

The `JobForm` handles the creation of the Job record, including related Company and Location records:

```python
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
```

### Viewing Job Listings

```python
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
```

### Editing and Deleting Jobs

The application includes views for editing and deleting jobs, with appropriate permission checks to ensure recruiters can only modify their own jobs.

## Candidate Management

Recruiters can view and manage applications for their job postings:

```python
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

        # Get all applications for this recruiter's jobs
        all_applications = Application.objects.filter(
            job__recruiter=recruiter_profile
        ).select_related('candidate', 'job')

        # Calculate status counts
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
```

### Updating Application Status

Recruiters can update the status of applications:

```python
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
```

## AI Recommendations

One of the most powerful features for recruiters is AI-powered candidate recommendations:

```python
@login_required
def ai_recommendations(request):
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

        # Get all active jobs for this recruiter
        jobs = Job.objects.filter(
            recruiter=recruiter_profile,
            status='Open'
        ).select_related('company', 'company__location').order_by('-posted_date')

        # Get job seekers with complete profiles
        job_seekers = JobSeekerProfile.objects.filter(
            skills__isnull=False,  # Must have skills
        ).select_related('user')

        # Filter by selected job if provided
        selected_job_id = request.GET.get('job', '')
        selected_job = None
        recommendations = []

        if selected_job_id:
            try:
                selected_job = Job.objects.get(id=selected_job_id, recruiter=recruiter_profile)

                # Check if we already have cached recommendations for this job
                cache_key = f"job_recommendations_{selected_job.id}"
                cached_recommendations = cache.get(cache_key)

                if cached_recommendations:
                    # Use cached recommendations
                    recommendations = cached_recommendations

                    # Get the actual JobSeekerProfile objects for the recommendations
                    if recommendations:
                        # Extract candidate IDs from recommendations
                        candidate_ids = [rec.get('candidate_id') for rec in recommendations if 'candidate_id' in rec]

                        # Get the profiles for these candidates
                        recommended_profiles = JobSeekerProfile.objects.filter(
                            id__in=candidate_ids
                        ).select_related('user')

                        # Create a mapping of profile ID to profile object
                        profile_map = {str(profile.id): profile for profile in recommended_profiles}

                        # Add the profile object to each recommendation
                        for rec in recommendations:
                            if 'candidate_id' in rec and str(rec['candidate_id']) in profile_map:
                                rec['profile'] = profile_map[str(rec['candidate_id'])]
                else:
                    # Generate new AI recommendations for this job
                    ai_recommendations = generate_candidate_recommendations(selected_job, job_seekers)

                    # Process recommendations and add profiles
                    if ai_recommendations:
                        candidate_ids = [rec.get('candidate_id') for rec in ai_recommendations if 'candidate_id' in rec]
                        recommended_profiles = JobSeekerProfile.objects.filter(
                            id__in=candidate_ids
                        ).select_related('user')
                        profile_map = {str(profile.id): profile for profile in recommended_profiles}

                        for rec in ai_recommendations:
                            if 'candidate_id' in rec and str(rec['candidate_id']) in profile_map:
                                rec['profile'] = profile_map[str(rec['candidate_id'])]

                        # Cache recommendations
                        cache.set(cache_key, ai_recommendations, 86400)  # Cache for 24 hours
                        recommendations = ai_recommendations
            except Job.DoesNotExist:
                messages.error(request, "Selected job not found.")

    except Exception as e:
        jobs = []
        job_seekers = []
        recommendations = []
        selected_job = None
        messages.error(request, f"Error loading recommendations: {str(e)}")

    context = {
        'jobs': jobs,
        'selected_job': selected_job,
        'recommendations': recommendations,
        'total_jobs': len(jobs) if jobs else 0,
        'total_job_seekers': job_seekers.count() if job_seekers else 0
    }

    return render(request, 'ai_recommendations.html', context)
```

The `generate_candidate_recommendations` function in `utils.py` handles the AI analysis:

```python
def generate_candidate_recommendations(job, job_seekers, limit=10):
    """
    Generate AI recommendations for candidates that match a specific job.

    Args:
        job (Job): The job to find candidates for
        job_seekers (QuerySet): QuerySet of JobSeekerProfile objects
        limit (int): Maximum number of recommendations to return

    Returns:
        list: List of candidate recommendations with match scores and insights
    """
    try:
        # Format the job description
        job_description = f"""
        Job Title: {job.job_title}
        Company: {job.company.name}
        Location: {job.company.location.city}, {job.company.location.state}, {job.company.location.country}
        Workplace Type: {job.workplace_type}
        Employment Type: {job.employment_type}
        Experience Required: {job.experience_required}
        
        Summary:
        {job.summary}
        
        Key Responsibilities:
        {', '.join(job.get_key_responsibilities())}
        
        Requirements:
        {', '.join(job.get_requirements())}
        
        Skills Required:
        {', '.join(job.get_skills_required())}
        """

        # Format candidate profiles
        candidate_profiles = []
        for profile in job_seekers[:limit]:  # Limit the number of profiles to process
            # Skip profiles without skills
            if not profile.skills:
                continue

            # Format the candidate profile
            candidate_profile = f"""
            Candidate ID: {profile.id}
            Skills: {profile.skills}
            Experience: {profile.experience_years} years
            Education: {profile.education if profile.education else 'Not specified'}
            Location: {profile.location if profile.location else 'Not specified'}
            """
            candidate_profiles.append(candidate_profile)

        # If no valid candidate profiles, return empty list
        if not candidate_profiles:
            logger.warning("No valid candidate profiles found for recommendations")
            return []

        # Join all candidate profiles
        all_profiles = "\n---\n".join(candidate_profiles)

        # Create the prompt
        prompt = RECRUITER_RECOMMENDATIONS_PROMPT.format(
            job_description=job_description,
            candidate_profiles=all_profiles
        )

        # Make the API call
        result = make_api_call(prompt)

        if not result or 'recommendations' not in result:
            logger.error("Failed to get candidate recommendations or invalid response format")
            return []

        return result['recommendations']

    except Exception as e:
        logger.error(f"Error generating candidate recommendations: {str(e)}")
        return []
```

## Shortlisted Candidates

Recruiters can view and manage shortlisted candidates:

```python
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
```

## Inviting Candidates

Recruiters can invite job seekers to apply for positions:

```python
@login_required
@require_POST
def invite_candidate(request):
    """Send an invitation to a candidate to apply for a job"""
    # Parse JSON data from request body
    try:
        data = json.loads(request.body)
        candidate_id = data.get('candidate_id')
        job_id = data.get('job_id')
        note = data.get('note', '')

        # Check if user is a recruiter
        try:
            user_type = UserType.objects.get(user=request.user)
            if not user_type.is_recruiter:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Only recruiters can send invitations'
                })
        except UserType.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User type not found'
            })

        # Get the job
        try:
            job = Job.objects.get(id=job_id)
            # Verify the job belongs to the recruiter
            if job.recruiter.user != request.user:
                return JsonResponse({
                    'status': 'error',
                    'message': 'You can only invite candidates to your own jobs'
                })
        except Job.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Job not found'
            })

        # Get the job seeker profile
        try:
            job_seeker_profile = JobSeekerProfile.objects.get(id=candidate_id)
            job_seeker = job_seeker_profile.user
        except JobSeekerProfile.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Candidate not found'
            })

        # Create the notification message
        company_name = job.company.name
        job_title = job.job_title

        message = f"You've been invited to apply for the {job_title} position at {company_name}."
        if note:
            message += f" Recruiter's note: {note}"

        # Create the notification
        related_link = f"/jobs/{job_id}/apply/"
        notification = create_notification(
            recipient=job_seeker,
            sender=request.user,
            message=message,
            notification_type='job',
            related_link=related_link
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Invitation sent to {job_seeker.get_full_name() or job_seeker.username} successfully!'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        })
    except Exception as e:
        logger.error(f"Error in invite_candidate view: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error sending invitation: {str(e)}'
        })
```

## Try It Yourself: Recruiter Workflow

Let's practice tracing a typical recruiter workflow:

1. Recruiter logs in and is redirected to the dashboard
2. Recruiter creates a new job posting
3. Job seekers apply to the job
4. Recruiter reviews applications and updates their status
5. Recruiter uses AI recommendations to find more candidates
6. Recruiter invites promising candidates to apply

Try to identify the views, templates, and models involved in each step of this workflow.

## Next Steps

In the next section, we'll explore the job seeker features of the application, including profile management, job search, and application tracking.
