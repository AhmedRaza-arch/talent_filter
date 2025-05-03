# 11. Testing and Debugging

## Understanding Testing and Debugging

In this section, we'll explore how to test and debug the Talent Filter application. Testing ensures that the application works as expected, while debugging helps identify and fix issues when they arise.

## Testing Approaches

The Talent Filter application can be tested using several approaches:

### Manual Testing

Manual testing involves interacting with the application as a user would:

1. **Functional Testing**: Verify that each feature works as expected
2. **Usability Testing**: Ensure the application is easy to use
3. **Compatibility Testing**: Check that the application works across different browsers and devices
4. **Performance Testing**: Verify that the application responds quickly and efficiently

### Automated Testing

Django provides tools for automated testing:

#### Unit Tests

Unit tests verify that individual components work correctly in isolation:

```python
# tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from talent_filter_app.models import UserType, Job, Company, Location

class UserTypeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.user_type = UserType.objects.get(user=self.user)
    
    def test_user_type_creation(self):
        """Test that a UserType is automatically created when a User is created"""
        self.assertIsNotNone(self.user_type)
        self.assertFalse(self.user_type.is_job_seeker)
        self.assertFalse(self.user_type.is_recruiter)
    
    def test_set_as_job_seeker(self):
        """Test setting a user as a job seeker"""
        self.user_type.is_job_seeker = True
        self.user_type.save()
        
        # Refresh from database
        self.user_type.refresh_from_db()
        
        self.assertTrue(self.user_type.is_job_seeker)
        self.assertFalse(self.user_type.is_recruiter)
    
    def test_set_as_recruiter(self):
        """Test setting a user as a recruiter"""
        self.user_type.is_recruiter = True
        self.user_type.save()
        
        # Refresh from database
        self.user_type.refresh_from_db()
        
        self.assertFalse(self.user_type.is_job_seeker)
        self.assertTrue(self.user_type.is_recruiter)
```

#### Integration Tests

Integration tests verify that components work together correctly:

```python
class JobCreationTest(TestCase):
    def setUp(self):
        # Create a user and set as recruiter
        self.user = User.objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='recruiterpassword'
        )
        self.user_type = UserType.objects.get(user=self.user)
        self.user_type.is_recruiter = True
        self.user_type.save()
        
        # Create a recruiter profile
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.user,
            role='HR Manager'
        )
    
    def test_job_creation(self):
        """Test creating a job with related objects"""
        # Create location
        location = Location.objects.create(
            city='San Francisco',
            state='California',
            country='USA'
        )
        
        # Create company
        company = Company.objects.create(
            name='Tech Corp',
            location=location
        )
        
        # Create job
        job = Job.objects.create(
            job_title='Software Engineer',
            company=company,
            workplace_type='Remote',
            employment_type='Full-time',
            experience_required='3-5 years',
            summary='We are looking for a talented software engineer...',
            recruiter=self.recruiter_profile,
            recruiter_name=self.user.get_full_name(),
            recruiter_position='HR Manager',
            application_link='https://example.com/apply',
            how_to_apply='Submit your resume and cover letter...'
        )
        
        # Set JSON fields
        job.set_key_responsibilities(['Develop new features', 'Fix bugs', 'Write tests'])
        job.set_requirements(['Python', 'Django', 'JavaScript'])
        job.set_skills_required(['Python', 'Django', 'JavaScript', 'React'])
        job.save()
        
        # Verify job was created
        self.assertEqual(Job.objects.count(), 1)
        
        # Verify relationships
        self.assertEqual(job.company, company)
        self.assertEqual(job.company.location, location)
        self.assertEqual(job.recruiter, self.recruiter_profile)
        
        # Verify JSON fields
        self.assertEqual(job.get_key_responsibilities(), ['Develop new features', 'Fix bugs', 'Write tests'])
        self.assertEqual(job.get_requirements(), ['Python', 'Django', 'JavaScript'])
        self.assertEqual(job.get_skills_required(), ['Python', 'Django', 'JavaScript', 'React'])
```

#### View Tests

View tests verify that views return the expected responses:

```python
class JobListingViewTest(TestCase):
    def setUp(self):
        # Create a user and set as recruiter
        self.user = User.objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='recruiterpassword'
        )
        self.user_type = UserType.objects.get(user=self.user)
        self.user_type.is_recruiter = True
        self.user_type.save()
        
        # Create a recruiter profile
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.user,
            role='HR Manager'
        )
        
        # Create location and company
        self.location = Location.objects.create(
            city='San Francisco',
            state='California',
            country='USA'
        )
        
        self.company = Company.objects.create(
            name='Tech Corp',
            location=self.location
        )
        
        # Create jobs
        for i in range(5):
            job = Job.objects.create(
                job_title=f'Software Engineer {i+1}',
                company=self.company,
                workplace_type='Remote',
                employment_type='Full-time',
                experience_required='3-5 years',
                summary=f'Job summary {i+1}',
                recruiter=self.recruiter_profile,
                recruiter_name=self.user.get_full_name(),
                recruiter_position='HR Manager',
                application_link='https://example.com/apply',
                how_to_apply='Submit your resume and cover letter...'
            )
            job.set_skills_required(['Python', 'Django', 'JavaScript'])
            job.save()
    
    def test_job_listings_view(self):
        """Test that the job listings view shows all jobs for the recruiter"""
        # Login as the recruiter
        self.client.login(username='recruiter', password='recruiterpassword')
        
        # Access the job listings page
        response = self.client.get('/job-listings/')
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that all jobs are in the context
        self.assertEqual(len(response.context['jobs']), 5)
        
        # Check that the correct template is used
        self.assertTemplateUsed(response, 'job_listings.html')
    
    def test_job_listings_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        # Access the job listings page without logging in
        response = self.client.get('/job-listings/')
        
        # Check that the response is a redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/job-listings/')
    
    def test_job_listings_view_wrong_user_type(self):
        """Test that job seekers are redirected to their dashboard"""
        # Create a job seeker
        job_seeker = User.objects.create_user(
            username='jobseeker',
            email='jobseeker@example.com',
            password='jobseekerpassword'
        )
        job_seeker_type = UserType.objects.get(user=job_seeker)
        job_seeker_type.is_job_seeker = True
        job_seeker_type.save()
        
        # Login as the job seeker
        self.client.login(username='jobseeker', password='jobseekerpassword')
        
        # Access the job listings page
        response = self.client.get('/job-listings/')
        
        # Check that the response is a redirect to job seeker dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/job-seeker-dashboard/')
```

#### Form Tests

Form tests verify that forms validate input correctly:

```python
class JobFormTest(TestCase):
    def setUp(self):
        # Create a user and set as recruiter
        self.user = User.objects.create_user(
            username='recruiter',
            email='recruiter@example.com',
            password='recruiterpassword'
        )
        self.user_type = UserType.objects.get(user=self.user)
        self.user_type.is_recruiter = True
        self.user_type.save()
        
        # Create a recruiter profile
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.user,
            role='HR Manager'
        )
    
    def test_job_form_valid(self):
        """Test that the job form validates correctly with valid data"""
        form_data = {
            'job_title': 'Software Engineer',
            'company_name': 'Tech Corp',
            'city': 'San Francisco',
            'state': 'California',
            'country': 'USA',
            'workplace_type': 'Remote',
            'employment_type': 'Full-time',
            'experience_required': '3-5 years',
            'summary': 'We are looking for a talented software engineer...',
            'key_responsibilities': 'Develop new features\nFix bugs\nWrite tests',
            'requirements': 'Python\nDjango\nJavaScript',
            'skills_required': 'Python, Django, JavaScript, React',
            'application_link': 'https://example.com/apply',
            'how_to_apply': 'Submit your resume and cover letter...',
            'recruiter_name': 'Recruiter Name',
            'recruiter_position': 'HR Manager',
            'recruiter_email': 'recruiter@example.com',
            'status': 'Open',
            'open_positions': 1
        }
        
        form = JobForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_job_form_invalid(self):
        """Test that the job form validates correctly with invalid data"""
        # Missing required fields
        form_data = {
            'job_title': '',  # Required field is empty
            'company_name': 'Tech Corp',
            'city': 'San Francisco',
            'state': 'California',
            'country': 'USA',
            'workplace_type': 'Remote',
            'employment_type': 'Full-time',
            'experience_required': '3-5 years',
            'summary': 'We are looking for a talented software engineer...',
            'key_responsibilities': 'Develop new features\nFix bugs\nWrite tests',
            'requirements': 'Python\nDjango\nJavaScript',
            'skills_required': 'Python, Django, JavaScript, React',
            'application_link': 'https://example.com/apply',
            'how_to_apply': 'Submit your resume and cover letter...',
            'recruiter_name': 'Recruiter Name',
            'recruiter_position': 'HR Manager',
            'recruiter_email': 'recruiter@example.com',
            'status': 'Open',
            'open_positions': 1
        }
        
        form = JobForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('job_title', form.errors)
```

### Running Tests

To run tests, use the Django test command:

```bash
python manage.py test
```

To run specific tests:

```bash
python manage.py test talent_filter_app.tests.UserTypeModelTest
```

To run tests with coverage:

```bash
coverage run --source='.' manage.py test
coverage report
```

## Debugging Techniques

When issues arise, several debugging techniques can help identify and fix them:

### Django Debug Toolbar

The Django Debug Toolbar provides insights into the application's performance and behavior:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]
```

```python
# urls.py
from django.conf import settings
from django.urls import include, path

urlpatterns = [
    # ...
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

### Logging

Django's logging system can help track down issues:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'talent_filter_app': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

Using logging in code:

```python
import logging

logger = logging.getLogger(__name__)

def extract_resume_data_from_api(resume_file_path, user_id=None):
    """
    Call an external API to extract data from a resume file.
    """
    try:
        logger.info(f"Starting resume extraction for user {user_id}")
        
        # ... extraction code ...
        
        logger.info(f"Resume extraction completed for user {user_id}")
        return processed_data
    except Exception as e:
        logger.error(f"Error extracting resume data: {str(e)}")
        return None
```

### Django Shell

The Django shell provides an interactive environment for debugging:

```bash
python manage.py shell
```

```python
# Example shell session
from talent_filter_app.models import Job, Company, Location
from django.contrib.auth.models import User

# Check if a user exists
User.objects.filter(username='testuser').exists()

# Examine a job's relationships
job = Job.objects.first()
job.company.name
job.company.location.city

# Test a function
from talent_filter_app.utils import read_resume_file
resume_text = read_resume_file('/path/to/resume.pdf')
print(resume_text[:100])
```

### Browser Developer Tools

Browser developer tools are essential for debugging frontend issues:

1. **Console**: View JavaScript errors and log messages
2. **Network**: Monitor HTTP requests and responses
3. **Elements**: Inspect and modify HTML and CSS
4. **Sources**: Debug JavaScript code
5. **Application**: Examine cookies, local storage, and session storage

### Common Issues and Solutions

#### Database Migrations

If you encounter database migration issues:

```bash
# Reset migrations (development only)
python manage.py migrate talent_filter_app zero
python manage.py makemigrations talent_filter_app
python manage.py migrate talent_filter_app

# Show migration status
python manage.py showmigrations

# Fake migrations
python manage.py migrate --fake
```

#### Static Files

If static files aren't loading:

```bash
# Collect static files
python manage.py collectstatic

# Check static file settings
# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

#### Form Validation

If forms aren't validating correctly:

```python
# Print form errors
form = JobForm(request.POST, user=request.user)
if not form.is_valid():
    print(form.errors)
```

#### AJAX Issues

If AJAX requests aren't working:

1. Check the browser console for errors
2. Verify that the CSRF token is included in the request
3. Check that the URL is correct
4. Verify that the view is returning the expected response

```javascript
// Include CSRF token in AJAX requests
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
})
.then(response => {
    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
})
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## Try It Yourself: Testing and Debugging

Let's practice testing and debugging:

1. Write a simple unit test for a model
2. Use the Django shell to explore the database
3. Add logging to a view function
4. Use browser developer tools to debug a frontend issue

## Next Steps

In the next section, we'll explore deployment considerations for the Talent Filter application.
