from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import json

class UserType(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_job_seeker = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)

    def __str__(self):
        if self.is_job_seeker:
            return f"{self.user.username} (Job Seeker)"
        elif self.is_recruiter:
            return f"{self.user.username} (Recruiter)"
        return self.user.username

class Location(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"

class Company(models.Model):
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

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
    recruiter = models.ForeignKey('RecruiterProfile', on_delete=models.CASCADE, related_name='jobs')
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

    def __str__(self):
        return self.job_title

    def set_key_responsibilities(self, responsibilities_list):
        self.key_responsibilities = json.dumps(responsibilities_list)

    def get_key_responsibilities(self):
        if self.key_responsibilities:
            return json.loads(self.key_responsibilities)
        return []

    def set_requirements(self, requirements_list):
        self.requirements = json.dumps(requirements_list)

    def get_requirements(self):
        if self.requirements:
            return json.loads(self.requirements)
        return []

    def set_nice_to_have(self, nice_to_have_list):
        if nice_to_have_list:
            self.nice_to_have = json.dumps(nice_to_have_list)

    def get_nice_to_have(self):
        if self.nice_to_have:
            return json.loads(self.nice_to_have)
        return []

    def set_skills_required(self, skills_list):
        self.skills_required = json.dumps(skills_list)

    def get_skills_required(self):
        if self.skills_required:
            return json.loads(self.skills_required)
        return []

    def set_external_portals(self, portals_list):
        if portals_list:
            self.external_portals = json.dumps(portals_list)

    def get_external_portals(self):
        if self.external_portals:
            return json.loads(self.external_portals)
        return []

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    skill_match = models.IntegerField()
    experience = models.FloatField()
    location = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='candidate_photos/', null=True, blank=True)
    resume = models.FileField(upload_to='candidate_resumes/', null=True, blank=True)

    def __str__(self):
        return self.name

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

    def __str__(self):
        return f"{self.candidate.name} - {self.job.title}"

class Metrics(models.Model):
    date = models.DateField(auto_now_add=True)
    total_jobs_posted = models.IntegerField()
    pending_applications = models.IntegerField()
    shortlisted_candidates = models.IntegerField()
    ai_suggested_matches = models.IntegerField()

    def __str__(self):
        return f"Metrics for {self.date}"

class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='recruiter_photos/', null=True, blank=True)
    role = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='job_seeker_photos/', null=True, blank=True)
    resume = models.FileField(upload_to='job_seeker_resumes/', null=True, blank=True)
    skills = models.TextField(blank=True, null=True)
    experience_years = models.FloatField(default=0)
    education = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username

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

    def __str__(self):
        return f"{self.notification_type} notification for {self.recipient.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserType for new users"""
    if created:
        UserType.objects.create(user=instance)
