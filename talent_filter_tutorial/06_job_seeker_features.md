# 6. Job Seeker Features

## Understanding the Job Seeker Experience

In this section, we'll explore the features available to job seekers in the Talent Filter application. Job seekers can create profiles, search for jobs, apply to positions, and use AI to analyze how well they match with job requirements.

## Job Seeker Dashboard

The job seeker dashboard provides an overview of available jobs, application status, and profile completion:

```python
@login_required
def job_seeker_dashboard(request):
    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
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
```

The dashboard template (`job_seeker_dashboard.html`) displays:
- Profile completion percentage
- Recent job listings
- Recent applications
- Quick links to search for jobs and manage applications

## Profile Management

Job seekers can create and update their profiles, including uploading resumes and profile pictures:

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

    # Calculate profile completion percentage
    profile_completion = calculate_profile_completion(request.user, job_seeker_profile)

    # Check if this is a new profile with minimal information
    is_new_profile = (profile_completion < 25)

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
            # Check if this is the upload form or the professional info form
            is_upload_form = 'upload-form' in request.POST.get('form_id', '')

            if is_upload_form:
                # Handle file uploads directly
                if 'profile_picture' in request.FILES:
                    job_seeker_profile.profile_picture = request.FILES['profile_picture']
                    print(f"Uploaded profile picture: {job_seeker_profile.profile_picture.name}")

                if 'resume' in request.FILES:
                    job_seeker_profile.resume = request.FILES['resume']
                    print(f"Uploaded resume: {job_seeker_profile.resume.name}")
                    # Suggest using AI extraction
                    messages.info(request, "Resume uploaded! Use the 'Extract Data with AI' button to automatically fill your profile.")

                job_seeker_profile.save()
                messages.success(request, "Files uploaded successfully!")
            else:
                # Handle professional info update (excluding file fields)
                profile_form = JobSeekerProfileForm(request.POST, instance=job_seeker_profile)
                if profile_form.is_valid():
                    profile = profile_form.save(commit=False)
                    # Don't touch the file fields
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
        'is_new_profile': is_new_profile,
    }

    return render(request, 'job_seeker_profile.html', context)
```

### AI-Powered Resume Data Extraction

One of the most powerful features for job seekers is the ability to extract data from their resume using AI:

```python
@login_required
def extract_resume_data(request):
    """Extract data from resume using AI"""
    import time
    import logging
    import threading

    logger = logging.getLogger(__name__)

    # Check if user is a job seeker
    try:
        user_type = UserType.objects.get(user=request.user)
        if not user_type.is_job_seeker:
            return redirect('dashboard')
    except UserType.DoesNotExist:
        pass

    # For AJAX requests to check status
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'GET':
        # Return the current extraction status
        status_data = get_extraction_status(request.user.id)
        return JsonResponse(status_data)

    # Get job seeker profile
    try:
        job_seeker_profile = JobSeekerProfile.objects.get(user=request.user)

        # Check if resume exists
        if not job_seeker_profile.resume:
            messages.error(request, "Please upload a resume before using the AI extraction feature.")
            return redirect('job_seeker_profile')

        # Define a function to run the extraction process in a background thread
        def run_extraction_process():
            try:
                # Call the extraction function with user_id for status tracking
                resume_path = str(job_seeker_profile.resume)
                extracted_data = extract_resume_data_from_api(resume_path, user_id=request.user.id)

                if not extracted_data:
                    logger.error("Resume data extraction failed")
                    return

                # Update the profile with extracted data
                if 'skills' in extracted_data and extracted_data['skills']:
                    job_seeker_profile.skills = extracted_data['skills']

                if 'education' in extracted_data and extracted_data['education']:
                    job_seeker_profile.education = extracted_data['education']

                if 'experience_years' in extracted_data and extracted_data['experience_years']:
                    job_seeker_profile.experience_years = extracted_data['experience_years']

                if 'location' in extracted_data and extracted_data['location']:
                    job_seeker_profile.location = extracted_data['location']

                job_seeker_profile.save()

            except Exception as e:
                logger.error(f"Error in extraction thread: {str(e)}")

        # Start the extraction process in a background thread
        extraction_thread = threading.Thread(target=run_extraction_process)
        extraction_thread.daemon = True
        extraction_thread.start()

        # If this is an AJAX request, return a processing status
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'processing',
                'message': 'Resume extraction has started. Please wait...'
            })

        # For non-AJAX requests, redirect to the profile page with a message
        messages.info(request, "Resume extraction has started. This may take a minute...")
        return redirect('job_seeker_profile')

    except JobSeekerProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('job_seeker_profile')
    except Exception as e:
        logger.error(f"Error in extract_resume_data view: {str(e)}")
        messages.error(request, f"Error extracting data: {str(e)}")
        return redirect('job_seeker_profile')
```

The extraction process is handled by the `extract_resume_data_from_api` function in `utils.py`, which makes API calls to extract skills, education, experience, and location information from the resume.

## Job Search

Job seekers can browse and search for available jobs:

```python
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
```

## Applying for Jobs

Job seekers can apply to jobs they're interested in:

```python
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
```

## Application Management

Job seekers can view and manage their applications:

```python
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
```

Job seekers can also withdraw applications:

```python
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
```

## Job Match Analysis

One of the most powerful features for job seekers is the ability to analyze how well their resume matches a job description:

```python
def analyze_job_match(request, job_id):
    """Analyze the match between a job seeker's resume and a job description"""
    import logging
    import time

    logger = logging.getLogger(__name__)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] ===== ANALYZE_JOB_MATCH VIEW CALLED =====")
    logger.info(f"[{timestamp}] User: {request.user}, Job ID: {job_id}")
    logger.info(f"[{timestamp}] Request method: {request.method}")
    logger.info(f"[{timestamp}] Is AJAX: {'X-Requested-With' in request.headers}")

    if 'check_status' in request.GET:
        logger.info(f"[{timestamp}] Status check requested")

    # For testing purposes, we'll skip the user type check
    if request.path.startswith('/test-ai-match'):
        logger.info("Test page detected, skipping user type check")
    else:
        # Check if user is logged in
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'You must be logged in to analyze job matches'})

        # Check if user is a job seeker
        try:
            user_type = UserType.objects.get(user=request.user)
            if not user_type.is_job_seeker:
                return JsonResponse({'status': 'error', 'message': 'Only job seekers can analyze job matches'})
        except UserType.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User type not found'})

    # Get the job
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Job not found'})

    # Check if this is a status check request
    if request.GET.get('check_status') == 'true':
        # Get the current status from the cache
        status_data = get_job_match_status(request.user.id, job_id)

        if not status_data:
            return JsonResponse({
                'status': 'error',
                'message': 'No job match analysis in progress'
            })

        # Return the current status
        if status_data['status'] == JobMatchStatus.COMPLETED:
            return JsonResponse({
                'status': 'success',
                'result': status_data['result']
            })
        elif status_data['status'] == JobMatchStatus.FAILED:
            return JsonResponse({
                'status': 'error',
                'message': status_data.get('error_message', 'Failed to analyze job match')
            })
        else:
            # Still processing
            return JsonResponse({
                'status': 'processing',
                'message': 'Job match analysis is still in progress'
            })

    # Get job seeker profile and resume
    try:
        job_seeker_profile = JobSeekerProfile.objects.get(user=request.user)

        # Check if resume exists
        if not job_seeker_profile.resume:
            return JsonResponse({
                'status': 'error',
                'message': 'Please upload a resume before analyzing job matches'
            })

        # Read the resume file
        import os
        from django.conf import settings
        resume_path = os.path.join(settings.MEDIA_ROOT, str(job_seeker_profile.resume))
        logger.info(f"[{timestamp}] Resume path: {resume_path}")
        logger.info(f"[{timestamp}] Resume exists: {os.path.exists(resume_path)}")

        # Log resume file details
        if os.path.exists(resume_path):
            file_size = os.path.getsize(resume_path)
            logger.info(f"[{timestamp}] Resume file size: {file_size} bytes")
            logger.info(f"[{timestamp}] Resume file extension: {os.path.splitext(resume_path)[1]}")

        resume_text = read_resume_file(resume_path)
        logger.info(f"[{timestamp}] Resume text length: {len(resume_text)} characters")
        logger.info(f"[{timestamp}] Resume text starts with: {resume_text[:100]}...")

        if resume_text.startswith("Error:"):
            logger.error(f"[{timestamp}] Error reading resume: {resume_text}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error reading resume: {resume_text}'
            })
    except JobSeekerProfile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Profile not found'})
    except Exception as e:
        logger.error(f"Error in analyze_job_match view: {str(e)}")
        return JsonResponse({'status': 'error', 'message': f'Error analyzing job match: {str(e)}'})

    # Prepare job description text
    job_description = f"""Job Title: {job.job_title}
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

    # For testing purposes, use a fixed user ID
    user_id = request.user.id if request.user.is_authenticated else 999

    # Start the asynchronous job match analysis
    process_job_match_analysis_async(
        user_id,
        job_id,
        resume_text,
        job_description,
        analyze_resume_job_match
    )

    # Return immediately with a processing status
    return JsonResponse({
        'status': 'processing',
        'message': 'Job match analysis has started. Please wait while we analyze your resume against this job.'
    })
```

The analysis is performed asynchronously using the `process_job_match_analysis_async` function in `async_utils.py`, which calls the `analyze_resume_job_match` function in `utils.py`.

## Try It Yourself: Job Seeker Workflow

Let's practice tracing a typical job seeker workflow:

1. Job seeker registers and is redirected to the profile page
2. Job seeker uploads a resume and uses AI to extract information
3. Job seeker browses available jobs
4. Job seeker views a job and analyzes their match
5. Job seeker applies to the job
6. Job seeker tracks the application status

Try to identify the views, templates, and models involved in each step of this workflow.

## Next Steps

In the next section, we'll explore the AI integration in more detail, including how the application uses the Google Gemini API for resume parsing and job matching.
