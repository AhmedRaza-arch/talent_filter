from django.urls import path
from . import views

urlpatterns = [
    # Recruiter URLs
    path('', views.dashboard, name='dashboard'),
    path('job-listings/', views.job_listings, name='job_listings'),
    path('job-listings/add/', views.add_job, name='add_job'),
    path('job-listings/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('job-listings/<int:job_id>/view/', views.view_job, name='view_job'),
    path('job-listings/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('job-listings/<int:job_id>/update-status/', views.update_job_status, name='update_job_status'),
    path('job-listings/<int:job_id>/analyze-match/', views.analyze_job_match, name='analyze_job_match'),
    path('applications/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
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
    path('job-seeker-profile/extract-resume/', views.extract_resume_data, name='extract_resume_data'),
    path('jobs/<int:job_id>/apply/', views.apply_to_job, name='apply_to_job'),
    path('applications/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),

    # Notification URLs
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
]
