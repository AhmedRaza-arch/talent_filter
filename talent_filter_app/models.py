from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class Job(models.Model):
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    open_positions = models.IntegerField()
    posted_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Open', 'Open'), ('Closed', 'Closed')])

    def __str__(self):
        return self.title

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

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserType for new users"""
    if created:
        UserType.objects.create(user=instance)
