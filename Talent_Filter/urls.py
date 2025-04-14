from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from talent_filter_app import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('talent_filter_app.urls')),
    path('accounts/login/', app_views.login_view, name='login'),
    path('accounts/logout/', app_views.logout_view, name='logout'),
    path('accounts/signup/recruiter/', app_views.recruiter_signup, name='recruiter_signup'),
    path('accounts/signup/job-seeker/', app_views.job_seeker_signup, name='job_seeker_signup'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
