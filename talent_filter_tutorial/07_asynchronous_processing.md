# 7. Asynchronous Processing

## Understanding Asynchronous Operations

In this section, we'll explore how Talent Filter handles long-running operations asynchronously. This approach prevents the user interface from freezing while waiting for operations to complete, providing a better user experience.

## Why Asynchronous Processing?

Several operations in Talent Filter can take a significant amount of time to complete:

1. **Resume parsing**: Extracting information from resumes using AI
2. **Job matching**: Analyzing how well a resume matches a job description
3. **Candidate recommendations**: Generating AI-powered candidate recommendations

These operations involve:
- Reading and processing files
- Making API calls to external services
- Processing potentially large amounts of data

If these operations were performed synchronously (in the request-response cycle), users would experience long loading times and potentially timeout errors. Asynchronous processing solves these problems by:

1. Starting the operation in a background thread
2. Returning an immediate response to the user
3. Allowing the user to check the status of the operation
4. Notifying the user when the operation is complete

## Threading in Python

Talent Filter uses Python's `threading` module to perform operations in the background:

```python
import threading

# Define a function to run in the background
def background_task():
    # Perform long-running operation
    pass

# Create and start a thread
thread = threading.Thread(target=background_task)
thread.daemon = True  # Thread will exit when the main program exits
thread.start()
```

## Status Tracking with Cache

To track the status of asynchronous operations, Talent Filter uses Django's cache system:

```python
from django.core.cache import cache

# Cache timeout (in seconds)
CACHE_TIMEOUT = 3600  # 1 hour

# Cache key format
STATUS_KEY_FORMAT = "operation_status_{}"

def get_status_cache_key(user_id):
    """Generate a cache key for operation status"""
    return STATUS_KEY_FORMAT.format(user_id)

def get_operation_status(user_id):
    """Get the current operation status for a user"""
    cache_key = get_status_cache_key(user_id)
    status_data = cache.get(cache_key)
    
    if not status_data:
        # Initialize with default status
        status_data = {
            "status": "waiting",
            "progress": 0,
            "message": None,
            "result": None
        }
        
    return status_data

def update_operation_status(user_id, status=None, progress=None, message=None, result=None):
    """Update the operation status for a user"""
    cache_key = get_status_cache_key(user_id)
    status_data = get_operation_status(user_id)
    
    if status is not None:
        status_data["status"] = status
        
    if progress is not None:
        status_data["progress"] = progress
        
    if message is not None:
        status_data["message"] = message
        
    if result is not None:
        status_data["result"] = result
    
    # Save the updated status
    cache.set(cache_key, status_data, CACHE_TIMEOUT)
    
    return status_data
```

## Resume Extraction Example

Let's look at how asynchronous processing is used for resume extraction:

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

The extraction process updates the status at key points:

```python
def extract_resume_data_from_api(resume_file_path, user_id=None):
    """
    Call an external API to extract data from a resume file.

    Args:
        resume_file_path (str): Path to the resume file
        user_id (int, optional): User ID for tracking extraction status

    Returns:
        dict: Extracted data with keys 'skills', 'education', 'experience_years', 'location'
        or None if extraction failed
    """
    try:
        # Reset extraction status if user_id is provided
        if user_id:
            reset_extraction_status(user_id)
            update_extraction_status(
                user_id,
                overall_status=ExtractionStatus.ACTIVE,
                message="Starting resume extraction process..."
            )

        # Step 1: Reading the resume file
        if user_id:
            update_extraction_status(
                user_id,
                step=ExtractionStep.READING,
                status=ExtractionStatus.ACTIVE,
                message="Reading resume file..."
            )

        # ... read the file ...

        # Mark reading step as completed
        if user_id:
            update_extraction_status(
                user_id,
                step=ExtractionStep.READING,
                status=ExtractionStatus.COMPLETED,
                message="Resume file read successfully"
            )

        # Step 2: Extracting skills
        if user_id:
            update_extraction_status(
                user_id,
                step=ExtractionStep.SKILLS,
                status=ExtractionStatus.ACTIVE,
                message="Extracting skills from resume..."
            )

        # ... extract skills ...

        if user_id:
            if skills:
                update_extraction_status(
                    user_id,
                    step=ExtractionStep.SKILLS,
                    status=ExtractionStatus.COMPLETED,
                    message=f"Extracted {len(skills.split(','))} skills"
                )
            else:
                update_extraction_status(
                    user_id,
                    step=ExtractionStep.SKILLS,
                    status=ExtractionStatus.ERROR,
                    message="Failed to extract skills"
                )

        # ... continue with other steps ...

        # Final step: Update overall status
        if user_id:
            if has_some_data:
                update_extraction_status(
                    user_id,
                    message="Data extraction completed successfully",
                    extracted_data=processed_data,
                    overall_status=ExtractionStatus.COMPLETED,
                    progress=100  # Ensure progress is set to 100%
                )
            else:
                update_extraction_status(
                    user_id,
                    message="No data could be extracted from the resume",
                    overall_status=ExtractionStatus.ERROR
                )
                return None

        return processed_data

    except Exception as e:
        logger.error(f"Error extracting resume data: {str(e)}")
        if user_id:
            # Update the overall status to error
            update_extraction_status(
                user_id,
                overall_status=ExtractionStatus.ERROR,
                message=f"Error extracting resume data: {str(e)}",
                progress=100  # Set progress to 100% to indicate completion (even though it's an error)
            )
        return None
```

## Job Match Analysis Example

For job match analysis, the application uses a similar approach but with a dedicated module for asynchronous processing:

```python
def process_job_match_analysis_async(user_id, job_id, resume_text, job_description, analyze_func):
    """
    Process a job match analysis asynchronously.

    Args:
        user_id (int): The user ID
        job_id (int): The job ID
        resume_text (str): The resume text
        job_description (str): The job description
        analyze_func (callable): The function to call to analyze the match
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] ===== STARTING ASYNC JOB MATCH ANALYSIS =====")
    logger.info(f"[{timestamp}] User ID: {user_id}, Job ID: {job_id}")
    logger.info(f"[{timestamp}] Resume text length: {len(resume_text)} characters")
    logger.info(f"[{timestamp}] Job description length: {len(job_description)} characters")

    def _process_job_match():
        thread_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{thread_timestamp}] Thread started for job match analysis - User ID: {user_id}, Job ID: {job_id}")

        try:
            # Update status to processing
            set_job_match_status(user_id, job_id, JobMatchStatus.PROCESSING)
            logger.info(f"[{thread_timestamp}] Status set to PROCESSING")

            # Set a timeout for the analysis
            max_processing_time = 60  # 60 seconds max
            start_time = time.time()

            logger.info(f"[{thread_timestamp}] Calling analyze_func (analyze_resume_job_match)...")
            # Call the analysis function with the user_id
            result = analyze_func(resume_text, job_description, user_id=user_id)

            elapsed_time = time.time() - start_time
            logger.info(f"[{thread_timestamp}] analyze_func completed in {elapsed_time:.2f}s")

            # Check if we've exceeded the maximum processing time
            if elapsed_time > max_processing_time:
                logger.warning(f"[{thread_timestamp}] Job match analysis took too long ({elapsed_time:.2f}s)")

            if result:
                # Update status to completed with the result
                logger.info(f"[{thread_timestamp}] Analysis successful, setting status to COMPLETED")
                set_job_match_status(user_id, job_id, JobMatchStatus.COMPLETED, result=result)
                logger.info(f"[{thread_timestamp}] ===== ASYNC JOB MATCH ANALYSIS COMPLETED SUCCESSFULLY =====")
            else:
                # Update status to failed
                logger.error(f"[{thread_timestamp}] Analysis failed, setting status to FAILED")
                set_job_match_status(
                    user_id,
                    job_id,
                    JobMatchStatus.FAILED,
                    error_message="Failed to analyze job match after multiple attempts."
                )
                logger.error(f"[{thread_timestamp}] ===== ASYNC JOB MATCH ANALYSIS FAILED =====")
        except Exception as e:
            thread_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            logger.error(f"[{thread_timestamp}] Error processing job match analysis: {str(e)}")
            # Update status to failed with the error message
            set_job_match_status(
                user_id,
                job_id,
                JobMatchStatus.FAILED,
                error_message=f"Error: {str(e)}"
            )
            logger.error(f"[{thread_timestamp}] ===== ASYNC JOB MATCH ANALYSIS FAILED WITH EXCEPTION =====")

    # Start a new thread to process the job match analysis
    thread = threading.Thread(target=_process_job_match)
    thread.daemon = True
    thread.start()

    logger.info(f"[{timestamp}] Started background thread for job match analysis")

    # Return the initial status
    logger.info(f"[{timestamp}] Returning initial PENDING status")
    return set_job_match_status(user_id, job_id, JobMatchStatus.PENDING)
```

The status is tracked using a cache-based system:

```python
def get_job_match_cache_key(user_id, job_id):
    """Generate a cache key for a job match analysis"""
    return JOB_MATCH_CACHE_KEY_FORMAT.format(user_id, job_id)

def get_job_match_status(user_id, job_id):
    """Get the status of a job match analysis"""
    cache_key = get_job_match_cache_key(user_id, job_id)
    cached_data = cache.get(cache_key)

    if not cached_data:
        return None

    return cached_data

def set_job_match_status(user_id, job_id, status, result=None, error_message=None):
    """Set the status of a job match analysis"""
    cache_key = get_job_match_cache_key(user_id, job_id)

    cache_data = {
        'status': status,
        'updated_at': time.time()
    }

    if result:
        cache_data['result'] = result

    if error_message:
        cache_data['error_message'] = error_message

    cache.set(cache_key, cache_data, CACHE_TIMEOUT)

    return cache_data
```

## Client-Side Status Checking

The client-side JavaScript code periodically checks the status of asynchronous operations:

```javascript
// Example JavaScript for checking resume extraction status
function checkExtractionStatus() {
    $.ajax({
        url: '/job-seeker-profile/extract-resume/',
        type: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(data) {
            // Update progress bar
            $('#extraction-progress').css('width', data.progress + '%');
            
            // Update status message
            $('#extraction-status').text(data.message);
            
            if (data.overall_status === 'completed') {
                // Extraction completed successfully
                $('#extraction-container').addClass('is-success');
                
                // Update profile fields with extracted data
                if (data.extracted_data) {
                    if (data.extracted_data.skills) {
                        $('#id_skills').val(data.extracted_data.skills);
                    }
                    if (data.extracted_data.education) {
                        $('#id_education').val(data.extracted_data.education);
                    }
                    if (data.extracted_data.experience_years) {
                        $('#id_experience_years').val(data.extracted_data.experience_years);
                    }
                    if (data.extracted_data.location) {
                        $('#id_location').val(data.extracted_data.location);
                    }
                }
                
                // Stop checking status
                clearInterval(statusCheckInterval);
                
                // Show success message
                showNotification('Resume data extracted successfully!', 'success');
                
                // Enable the form
                $('#profile-form :input').prop('disabled', false);
                
            } else if (data.overall_status === 'error') {
                // Extraction failed
                $('#extraction-container').addClass('is-danger');
                
                // Stop checking status
                clearInterval(statusCheckInterval);
                
                // Show error message
                showNotification('Failed to extract resume data: ' + data.message, 'error');
                
                // Enable the form
                $('#profile-form :input').prop('disabled', false);
                
            } else {
                // Still processing, continue checking
                setTimeout(checkExtractionStatus, 2000);
            }
        },
        error: function() {
            // Error checking status
            $('#extraction-status').text('Error checking extraction status');
            
            // Stop checking status
            clearInterval(statusCheckInterval);
            
            // Enable the form
            $('#profile-form :input').prop('disabled', false);
        }
    });
}

// Start checking status when extraction begins
$('#extract-resume-btn').click(function() {
    // Disable the form while extraction is in progress
    $('#profile-form :input').prop('disabled', true);
    
    // Show the extraction progress container
    $('#extraction-container').removeClass('is-hidden');
    
    // Reset progress bar and status
    $('#extraction-progress').css('width', '0%');
    $('#extraction-status').text('Starting extraction...');
    
    // Start checking status
    setTimeout(checkExtractionStatus, 1000);
    
    // Send the extraction request
    $.ajax({
        url: '/job-seeker-profile/extract-resume/',
        type: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function(data) {
            // Initial response, status checking will handle the rest
        },
        error: function() {
            // Error starting extraction
            $('#extraction-status').text('Error starting extraction');
            
            // Enable the form
            $('#profile-form :input').prop('disabled', false);
        }
    });
});
```

## Extraction Status Model

The application uses a dedicated module for tracking extraction status:

```python
class ExtractionStep:
    """Extraction step constants"""
    READING = "reading"
    SKILLS = "skills"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    LOCATION = "location"
    SAVING = "saving"

class ExtractionStatus:
    """Extraction status constants"""
    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"

def get_extraction_cache_key(user_id):
    """Generate a cache key for extraction status"""
    return EXTRACTION_STATUS_KEY_FORMAT.format(user_id)

def get_extraction_status(user_id):
    """Get the current extraction status for a user"""
    cache_key = get_extraction_cache_key(user_id)
    status_data = cache.get(cache_key)
    
    if not status_data:
        # Initialize with default status
        status_data = {
            "overall_status": ExtractionStatus.WAITING,
            "steps": {
                ExtractionStep.READING: {"status": ExtractionStatus.WAITING, "message": None},
                ExtractionStep.SKILLS: {"status": ExtractionStatus.WAITING, "message": None},
                ExtractionStep.EDUCATION: {"status": ExtractionStatus.WAITING, "message": None},
                ExtractionStep.EXPERIENCE: {"status": ExtractionStatus.WAITING, "message": None},
                ExtractionStep.LOCATION: {"status": ExtractionStatus.WAITING, "message": None},
                ExtractionStep.SAVING: {"status": ExtractionStatus.WAITING, "message": None},
            },
            "progress": 0,
            "message": None,
            "extracted_data": None
        }
        
    return status_data

def update_extraction_status(user_id, step=None, status=None, message=None, progress=None, extracted_data=None, overall_status=None):
    """Update the extraction status for a user"""
    cache_key = get_extraction_cache_key(user_id)
    status_data = get_extraction_status(user_id)
    
    if step and status:
        status_data["steps"][step] = {
            "status": status,
            "message": message
        }
        
        # Update progress based on completed steps
        completed_steps = sum(1 for step_data in status_data["steps"].values() 
                             if step_data["status"] == ExtractionStatus.COMPLETED)
        status_data["progress"] = int((completed_steps / len(status_data["steps"])) * 100)
    
    if progress is not None:
        status_data["progress"] = progress
        
    if message is not None:
        status_data["message"] = message
        
    if extracted_data is not None:
        status_data["extracted_data"] = extracted_data
        
    if overall_status is not None:
        status_data["overall_status"] = overall_status
    
    # Save the updated status
    cache.set(cache_key, status_data, CACHE_TIMEOUT)
    
    return status_data

def reset_extraction_status(user_id):
    """Reset the extraction status for a user"""
    cache_key = get_extraction_cache_key(user_id)
    cache.delete(cache_key)
    return get_extraction_status(user_id)
```

## Job Match Status Model

Similarly, job match analysis has its own status tracking:

```python
class JobMatchStatus:
    """Status values for job match analysis"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

## Considerations for Production

In a production environment, there are several considerations for asynchronous processing:

1. **Thread Safety**: Ensure that background threads don't interfere with each other
2. **Resource Management**: Limit the number of concurrent threads to avoid overloading the server
3. **Error Handling**: Properly handle and log errors in background threads
4. **Timeouts**: Implement timeouts for long-running operations
5. **Scaling**: Consider using a dedicated task queue system (like Celery) for better scalability

## Try It Yourself: Asynchronous Processing Flow

Let's practice tracing the asynchronous processing flow:

1. User initiates an operation (e.g., resume extraction)
2. The view function starts a background thread and returns immediately
3. The client-side JavaScript periodically checks the status
4. The background thread updates the status as it progresses
5. When the operation completes, the status is updated with the result
6. The client-side JavaScript detects the completion and updates the UI

Try to identify the functions and models involved in each step of this flow.

## Next Steps

In the next section, we'll explore the notification system, which keeps users informed about important events in the application.
