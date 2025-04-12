from django.contrib import admin
from .models import UserType, Job, Candidate, Application, Metrics, RecruiterProfile, JobSeekerProfile

# Register your models here.
admin.site.register(UserType)
admin.site.register(Job)
admin.site.register(Candidate)
admin.site.register(Application)
admin.site.register(Metrics)
admin.site.register(RecruiterProfile)
admin.site.register(JobSeekerProfile)
