"""
Module for tracking resume extraction status.
"""
from django.core.cache import cache

# Cache timeout (in seconds)
CACHE_TIMEOUT = 3600  # 1 hour

# Cache key format
EXTRACTION_STATUS_KEY_FORMAT = "resume_extraction_status_{}"

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
