from django.urls import path
from . import views

urlpatterns = [
    # Recruiter URLs
    path('', views.dashboard, name='dashboard'),
    path('job-listings/', views.job_listings, name='job_listings'),
    path('candidate-management/', views.candidate_management, name='candidate_management'),
    path('ai-recommendations/', views.ai_recommendations, name='ai_recommendations'),
    path('shortlisted-candidates/', views.shortlisted_candidates, name='shortlisted_candidates'),
    path('reports-analytics/', views.reports_analytics, name='reports_analytics'),
    path('settings/', views.settings, name='settings'),

    # Job Seeker URLs - Fixed to avoid recursive patterns
    path('job-seeker-dashboard/', views.job_seeker_dashboard, name='job_seeker_dashboard'),
    path('available-jobs/', views.available_jobs, name='available_jobs'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('job-seeker-profile/', views.job_seeker_profile, name='job_seeker_profile'),
]
