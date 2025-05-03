"""
Utilities for handling asynchronous job processing.
"""
import threading
import time
import logging
import json
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache keys will be in the format: job_match_analysis_{user_id}_{job_id}
JOB_MATCH_CACHE_KEY_FORMAT = "job_match_analysis_{}__{}"

# Cache timeout (in seconds)
CACHE_TIMEOUT = 3600  # 1 hour

class JobMatchStatus:
    """Status values for job match analysis"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

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
