# 3. Database Models

## Understanding the Data Structure

In this section, we'll explore the database models that form the foundation of the Talent Filter application. Models define the structure of the data, relationships between different entities, and include methods that encapsulate business logic.

## Model Overview

Here's a diagram showing the main models and their relationships:

```
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│     User      │       │   UserType    │       │ RecruiterProfile │
│ (Django Auth) │◄──1:1─┤               │       │                │
└───────────────┘       │ is_job_seeker │◄─1:1──┤    user        │
        ▲                │ is_recruiter │       │    role        │
        │                └───────────────┘       │ company_name  │
        │                        ▲               └───────────────┘
        │                        │                       ▲
        │                        │                       │
┌───────────────┐               │                ┌──────┴────────┐
│JobSeekerProfile│◄──────1:1────┘                │               │
│                │                               │      Job      │
│    user        │                               │               │
│    skills      │                               │   job_title   │
│    resume      │                               │   company     │◄─┐
│    education   │                               │   recruiter   │  │
└───────────────┘                               └───────────────┘  │
        ▲                                               ▲          │
        │                                               │          │
        │                                               │          │
┌───────────────┐                               ┌───────┴───────┐ │
│   Candidate   │◄───────────────────────────1─┤  Application  │ │
│               │                               │               │ │
│     name      │                               │   candidate   │ │
│     role      │                               │      job      │ │
│  skill_match  │                               │    status     │ │
└───────────────┘                               └───────────────┘ │
                                                                  │
                                                ┌───────────────┐ │
                                                │    Company    │◄┘
                                                │               │
                                                │     name      │
                                                │   location    │◄─┐
                                                └───────────────┘ │
                                                                  │
                                                ┌───────────────┐ │
                                                │   Location    │◄┘
                                                │               │
                                                │     city      │
                                                │     state     │
                                                │    country    │
                                                └───────────────┘
```

## Key Models in Detail

Let's examine each key model in detail:

### User and Authentication Models

#### UserType

This model extends Django's built-in User model to specify whether a user is a job seeker or recruiter:

```python
class UserType(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_job_seeker = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)
```

- `user`: One-to-one relationship with Django's User model
- `is_job_seeker`: Boolean flag indicating if the user is a job seeker
- `is_recruiter`: Boolean flag indicating if the user is a recruiter

A signal handler automatically creates a UserType instance when a new User is created:

```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserType for new users"""
    if created:
        UserType.objects.create(user=instance)
```

#### RecruiterProfile

Stores additional information about recruiters:

```python
class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='recruiter_photos/', null=True, blank=True)
    role = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
```

#### JobSeekerProfile

Stores additional information about job seekers:

```python
class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='job_seeker_photos/', null=True, blank=True)
    resume = models.FileField(upload_to='job_seeker_resumes/', null=True, blank=True)
    skills = models.TextField(blank=True, null=True)
    experience_years = models.FloatField(default=0)
    education = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
```

### Job-Related Models

#### Location

Stores location information:

```python
class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
```

#### Company

Represents a company:

```python
class Company(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
```

#### Job

The central model for job listings:

```python
class Job(models.Model):
    # Job identification
    job_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    job_title = models.CharField(max_length=200)
    
    # Company information
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    
    # Employment details
    WORKPLACE_CHOICES = [
        ('On-site', 'On-site'),
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ]
    
    workplace_type = models.CharField(max_length=20, choices=WORKPLACE_CHOICES)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    experience_required = models.CharField(max_length=50)
    posted_date = models.DateField(auto_now_add=True)
    application_deadline = models.DateField(null=True, blank=True)
    
    # Job description
    summary = models.TextField()
    key_responsibilities = models.TextField()
    requirements = models.TextField()
    nice_to_have = models.TextField(blank=True, null=True)
    
    # Skills
    skills_required = models.TextField()
    
    # Recruiter information
    recruiter = models.ForeignKey('RecruiterProfile', on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)
    recruiter_name = models.CharField(max_length=100)
    recruiter_position = models.CharField(max_length=100)
    recruiter_email = models.EmailField(blank=True, null=True)
    recruiter_linkedin = models.URLField(blank=True, null=True)
    
    # Application information
    application_link = models.URLField()
    how_to_apply = models.TextField()
    external_portals = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[('Open', 'Open'), ('Closed', 'Closed')], default='Open')
    open_positions = models.IntegerField(default=1)
```

The Job model includes several helper methods for handling JSON-serialized fields:

```python
def set_key_responsibilities(self, responsibilities_list):
    self.key_responsibilities = json.dumps(responsibilities_list)

def get_key_responsibilities(self):
    if self.key_responsibilities:
        return json.loads(self.key_responsibilities)
    return []
```

Similar methods exist for requirements, nice_to_have, skills_required, and external_portals.

#### Candidate

Represents a job candidate:

```python
class Candidate(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    skill_match = models.IntegerField()
    experience = models.FloatField()
    location = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='candidate_photos/', null=True, blank=True)
    resume = models.FileField(upload_to='candidate_resumes/', null=True, blank=True)
```

#### Application

Tracks job applications:

```python
class Application(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[
        ('Pending Review', 'Pending Review'),
        ('Interview Scheduled', 'Interview Scheduled'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
        ('Hired', 'Hired')
    ])
    applied_date = models.DateField(auto_now_add=True)
```

### Communication Models

#### Notification

Stores notifications for users:

```python
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('application', 'Application Update'),
        ('message', 'New Message'),
        ('interview', 'Interview Invitation'),
        ('job', 'Job Update'),
        ('system', 'System Notification'),
    )
    
    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    related_link = models.CharField(max_length=255, blank=True, null=True)  # URL to redirect to when clicked
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
```

### AI-Related Models

#### JobMatchAnalysis

Tracks job match analysis requests and their status:

```python
class JobMatchAnalysis(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-updated_at']
```

#### CandidateRecommendation

Stores AI-generated candidate recommendations for jobs:

```python
class CandidateRecommendation(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='recommendations')
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='job_recommendations')
    match_score = models.IntegerField(default=0)
    matching_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    experience_match = models.TextField(blank=True, null=True)
    education_match = models.TextField(blank=True, null=True)
    overall_assessment = models.TextField(blank=True, null=True)
    contact_recommendation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('job', 'job_seeker')
        ordering = ['-match_score', '-updated_at']
```

## Model Relationships

Understanding the relationships between models is crucial:

1. **One-to-One Relationships**:
   - User to UserType
   - User to RecruiterProfile
   - User to JobSeekerProfile

2. **One-to-Many Relationships**:
   - RecruiterProfile to Job (one recruiter can post many jobs)
   - Job to Application (one job can have many applications)
   - Candidate to Application (one candidate can submit many applications)
   - User to Notification (one user can receive many notifications)

3. **Many-to-Many Relationships**:
   - There are no explicit many-to-many relationships in the current model structure

## Working with Models

Here are some common operations you'll perform with these models:

### Creating a New Job

```python
# Get the recruiter profile
recruiter_profile = RecruiterProfile.objects.get(user=request.user)

# Get or create location
location, _ = Location.objects.get_or_create(
    city='San Francisco',
    state='California',
    country='USA'
)

# Get or create company
company, _ = Company.objects.get_or_create(
    name='Tech Corp',
    defaults={'location': location}
)

# Create the job
job = Job.objects.create(
    job_title='Software Engineer',
    company=company,
    workplace_type='Remote',
    employment_type='Full-time',
    experience_required='3-5 years',
    summary='We are looking for a talented software engineer...',
    recruiter=recruiter_profile,
    recruiter_name=request.user.get_full_name(),
    recruiter_position='HR Manager',
    application_link='https://example.com/apply',
    how_to_apply='Submit your resume and cover letter...'
)

# Set JSON fields
job.set_key_responsibilities(['Develop new features', 'Fix bugs', 'Write tests'])
job.set_requirements(['Python', 'Django', 'JavaScript'])
job.set_skills_required(['Python', 'Django', 'JavaScript', 'React'])
job.save()
```

### Querying Jobs

```python
# Get all open jobs
open_jobs = Job.objects.filter(status='Open')

# Get jobs for a specific recruiter
recruiter_jobs = Job.objects.filter(recruiter=recruiter_profile)

# Get jobs with specific skills (using contains lookup)
python_jobs = Job.objects.filter(skills_required__contains='Python')

# Get recent jobs with related objects
recent_jobs = Job.objects.filter(status='Open').select_related('company', 'company__location').order_by('-posted_date')[:5]
```

### Working with Applications

```python
# Create an application
application = Application.objects.create(
    job=job,
    candidate=candidate,
    status='Pending Review'
)

# Update application status
application.status = 'Interview Scheduled'
application.save()

# Get applications for a job
job_applications = Application.objects.filter(job=job)

# Get applications by status
pending_applications = Application.objects.filter(status='Pending Review')
```

## Try It Yourself: Model Exploration

1. Look at the `models.py` file and identify any models we didn't cover in detail
2. Find all the choices fields (fields with predefined options)
3. Identify which models use JSONField or store JSON in TextField
4. Find all the models that have custom ordering defined in their Meta class
5. Identify which models might benefit from additional indexes for performance

## Next Steps

In the next section, we'll explore the authentication system and how user types are managed in the application.
