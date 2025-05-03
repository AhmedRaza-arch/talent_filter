# 8. Notification System

## Understanding the Notification System

In this section, we'll explore how Talent Filter keeps users informed about important events through its notification system. Notifications help users stay updated on application status changes, messages, and system announcements.

## Notification Model

The core of the notification system is the `Notification` model:

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

Key fields include:
- `recipient`: The user who receives the notification
- `sender`: The user who triggered the notification (optional)
- `message`: The notification text
- `notification_type`: The type of notification (application, message, etc.)
- `related_link`: A URL to redirect to when the notification is clicked
- `is_read`: Whether the notification has been read
- `created_at`: When the notification was created

## Creating Notifications

The application includes a utility function for creating notifications:

```python
def create_notification(recipient, message, notification_type, sender=None, related_link=None):
    """
    Create a notification for a user.

    Args:
        recipient (User): The user to notify
        message (str): The notification message
        notification_type (str): The type of notification (application, message, etc.)
        sender (User, optional): The user who triggered the notification
        related_link (str, optional): URL to redirect to when clicked

    Returns:
        Notification: The created notification
    """
    try:
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            message=message,
            notification_type=notification_type,
            related_link=related_link
        )
        return notification
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return None
```

## Notification Context Processor

To make notifications available in all templates, the application uses a context processor:

```python
# context_processors.py
def notifications(request):
    """Add unread notification count to context"""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        recent_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')[:5]
        
        return {
            'unread_notification_count': unread_count,
            'recent_notifications': recent_notifications
        }
    return {'unread_notification_count': 0, 'recent_notifications': []}
```

This is registered in `settings.py`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ...
                'talent_filter_app.context_processors.notifications',
            ],
        },
    },
]
```

## Notification Views

The application includes views for managing notifications:

```python
@login_required
def notifications_list(request):
    """View all notifications"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 10)  # Show 10 notifications per page
    page = request.GET.get('page')
    notifications_page = paginator.get_page(page)
    
    return render(request, 'notifications.html', {'notifications': notifications_page})

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # If this is an AJAX request, return a JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # If there's a related link, redirect to it
    if notification.related_link:
        return redirect(notification.related_link)
    
    # Otherwise, redirect back to the notifications list
    return redirect('notifications_list')

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    # If this is an AJAX request, return a JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # Redirect back to the notifications list
    return redirect('notifications_list')

@login_required
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    
    # If this is an AJAX request, return a JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # Redirect back to the notifications list
    return redirect('notifications_list')

@login_required
def delete_all_notifications(request):
    """Delete all notifications"""
    Notification.objects.filter(recipient=request.user).delete()
    
    # If this is an AJAX request, return a JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # Redirect back to the notifications list
    return redirect('notifications_list')
```

## Notification Templates

The application includes templates for displaying notifications:

### Notification Dropdown in Navigation

```html
<!-- Notification dropdown in navigation -->
<div class="navbar-item has-dropdown is-hoverable">
    <a class="navbar-link">
        <span class="icon">
            <i class="fas fa-bell"></i>
        </span>
        {% if unread_notification_count > 0 %}
        <span class="tag is-danger is-rounded notification-count">{{ unread_notification_count }}</span>
        {% endif %}
    </a>
    
    <div class="navbar-dropdown is-right">
        <div class="notification-header">
            <p class="has-text-weight-bold">Notifications</p>
            {% if unread_notification_count > 0 %}
            <a href="{% url 'mark_all_notifications_read' %}" class="mark-all-read">Mark all as read</a>
            {% endif %}
        </div>
        
        <div class="notification-list">
            {% if recent_notifications %}
                {% for notification in recent_notifications %}
                <a href="{% url 'mark_notification_read' notification.id %}" class="navbar-item notification-item">
                    <div class="notification-icon">
                        {% if notification.notification_type == 'application' %}
                            <span class="icon has-text-info"><i class="fas fa-file-alt"></i></span>
                        {% elif notification.notification_type == 'message' %}
                            <span class="icon has-text-success"><i class="fas fa-envelope"></i></span>
                        {% elif notification.notification_type == 'interview' %}
                            <span class="icon has-text-warning"><i class="fas fa-calendar-alt"></i></span>
                        {% elif notification.notification_type == 'job' %}
                            <span class="icon has-text-primary"><i class="fas fa-briefcase"></i></span>
                        {% else %}
                            <span class="icon has-text-grey"><i class="fas fa-info-circle"></i></span>
                        {% endif %}
                    </div>
                    <div class="notification-content">
                        <p class="notification-message">{{ notification.message }}</p>
                        <p class="notification-time">{{ notification.created_at|timesince }} ago</p>
                    </div>
                </a>
                {% endfor %}
                {% if unread_notification_count > 5 %}
                <a href="{% url 'notifications_list' %}" class="navbar-item view-all">
                    View all notifications
                </a>
                {% endif %}
            {% else %}
                <div class="navbar-item">
                    <p>No new notifications</p>
                </div>
            {% endif %}
        </div>
    </div>
</div>
```

### Notifications List Page

```html
<!-- notifications.html -->
{% extends 'base1.html' %}

{% block content %}
<div class="container">
    <div class="section">
        <h1 class="title">Notifications</h1>
        
        <div class="notification-actions">
            {% if notifications %}
                <a href="{% url 'mark_all_notifications_read' %}" class="button is-primary">
                    <span class="icon"><i class="fas fa-check-double"></i></span>
                    <span>Mark All as Read</span>
                </a>
                <a href="{% url 'delete_all_notifications' %}" class="button is-danger">
                    <span class="icon"><i class="fas fa-trash"></i></span>
                    <span>Delete All</span>
                </a>
            {% endif %}
        </div>
        
        <div class="notification-list-container">
            {% if notifications %}
                {% for notification in notifications %}
                <div class="notification-card {% if not notification.is_read %}unread{% endif %}">
                    <div class="notification-icon">
                        {% if notification.notification_type == 'application' %}
                            <span class="icon has-text-info"><i class="fas fa-file-alt"></i></span>
                        {% elif notification.notification_type == 'message' %}
                            <span class="icon has-text-success"><i class="fas fa-envelope"></i></span>
                        {% elif notification.notification_type == 'interview' %}
                            <span class="icon has-text-warning"><i class="fas fa-calendar-alt"></i></span>
                        {% elif notification.notification_type == 'job' %}
                            <span class="icon has-text-primary"><i class="fas fa-briefcase"></i></span>
                        {% else %}
                            <span class="icon has-text-grey"><i class="fas fa-info-circle"></i></span>
                        {% endif %}
                    </div>
                    <div class="notification-content">
                        <p class="notification-message">{{ notification.message }}</p>
                        <p class="notification-meta">
                            <span class="notification-time">{{ notification.created_at|date:"F j, Y, g:i a" }}</span>
                            {% if notification.sender %}
                            <span class="notification-sender">from {{ notification.sender.get_full_name|default:notification.sender.username }}</span>
                            {% endif %}
                        </p>
                    </div>
                    <div class="notification-actions">
                        {% if not notification.is_read %}
                        <a href="{% url 'mark_notification_read' notification.id %}" class="button is-small is-primary">
                            <span class="icon"><i class="fas fa-check"></i></span>
                        </a>
                        {% endif %}
                        {% if notification.related_link %}
                        <a href="{{ notification.related_link }}" class="button is-small is-info">
                            <span class="icon"><i class="fas fa-external-link-alt"></i></span>
                        </a>
                        {% endif %}
                        <a href="{% url 'delete_notification' notification.id %}" class="button is-small is-danger">
                            <span class="icon"><i class="fas fa-trash"></i></span>
                        </a>
                    </div>
                </div>
                {% endfor %}
                
                <!-- Pagination -->
                {% if notifications.has_other_pages %}
                <nav class="pagination is-centered" role="navigation" aria-label="pagination">
                    {% if notifications.has_previous %}
                    <a href="?page={{ notifications.previous_page_number }}" class="pagination-previous">Previous</a>
                    {% else %}
                    <a class="pagination-previous" disabled>Previous</a>
                    {% endif %}
                    
                    {% if notifications.has_next %}
                    <a href="?page={{ notifications.next_page_number }}" class="pagination-next">Next</a>
                    {% else %}
                    <a class="pagination-next" disabled>Next</a>
                    {% endif %}
                    
                    <ul class="pagination-list">
                        {% for i in notifications.paginator.page_range %}
                        <li>
                            {% if notifications.number == i %}
                            <a class="pagination-link is-current" aria-label="Page {{ i }}" aria-current="page">{{ i }}</a>
                            {% else %}
                            <a href="?page={{ i }}" class="pagination-link" aria-label="Go to page {{ i }}">{{ i }}</a>
                            {% endif %}
                        </li>
                        {% endfor %}
                    </ul>
                </nav>
                {% endif %}
                
            {% else %}
                <div class="notification is-info">
                    <p>You don't have any notifications yet.</p>
                </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

## JavaScript for Notifications

The application includes JavaScript for handling notifications:

```javascript
// Mark notification as read via AJAX
$('.notification-item').click(function(e) {
    e.preventDefault();
    
    var notificationId = $(this).data('notification-id');
    var url = $(this).attr('href');
    
    $.ajax({
        url: '/notifications/' + notificationId + '/mark-read/',
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(data) {
            // If there's a related link, redirect to it
            if (data.related_link) {
                window.location.href = data.related_link;
            } else {
                // Otherwise, update the UI
                updateNotificationCount();
            }
        }
    });
});

// Mark all notifications as read via AJAX
$('.mark-all-read').click(function(e) {
    e.preventDefault();
    
    $.ajax({
        url: '/notifications/mark-all-read/',
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function() {
            // Update the UI
            updateNotificationCount();
            $('.notification-item').removeClass('unread');
        }
    });
});

// Update notification count
function updateNotificationCount() {
    $.ajax({
        url: '/notifications/count/',
        type: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(data) {
            var count = data.count;
            
            if (count > 0) {
                $('.notification-count').text(count).show();
            } else {
                $('.notification-count').hide();
            }
        }
    });
}

// Poll for new notifications every 60 seconds
setInterval(updateNotificationCount, 60000);
```

## Notification Styling

The application includes CSS for styling notifications:

```css
/* Notification dropdown */
.notification-count {
    position: absolute;
    top: 0;
    right: 0;
    font-size: 0.7rem;
    transform: translate(25%, -25%);
}

.notification-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #f5f5f5;
}

.notification-list {
    max-height: 300px;
    overflow-y: auto;
}

.notification-item {
    display: flex;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #f5f5f5;
    transition: background-color 0.2s;
}

.notification-item:hover {
    background-color: #f5f5f5;
}

.notification-item.unread {
    background-color: #f0f8ff;
}

.notification-icon {
    margin-right: 0.5rem;
    display: flex;
    align-items: center;
}

.notification-content {
    flex: 1;
}

.notification-message {
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.notification-time {
    font-size: 0.7rem;
    color: #888;
}

.view-all {
    text-align: center;
    font-weight: bold;
}

/* Notification list page */
.notification-list-container {
    margin-top: 1rem;
}

.notification-card {
    display: flex;
    padding: 1rem;
    border: 1px solid #f5f5f5;
    border-radius: 4px;
    margin-bottom: 1rem;
    transition: background-color 0.2s;
}

.notification-card.unread {
    background-color: #f0f8ff;
    border-left: 4px solid #3273dc;
}

.notification-card .notification-icon {
    font-size: 1.5rem;
    margin-right: 1rem;
}

.notification-card .notification-content {
    flex: 1;
}

.notification-card .notification-message {
    font-size: 1rem;
    margin-bottom: 0.5rem;
}

.notification-card .notification-meta {
    font-size: 0.8rem;
    color: #888;
}

.notification-card .notification-actions {
    display: flex;
    align-items: center;
}

.notification-card .notification-actions .button {
    margin-left: 0.5rem;
}

.notification-actions {
    margin-bottom: 1rem;
}
```

## Notification Examples

Here are some examples of how notifications are created in different parts of the application:

### Application Status Update

```python
@login_required
def update_application_status(request, application_id):
    # ... code to update application status ...
    
    # Create notification for the job seeker
    try:
        # Find the candidate's user
        job_seekers = User.objects.filter(jobseekerprofile__isnull=False)
        for job_seeker in job_seekers:
            if job_seeker.get_full_name() == application.candidate.name or job_seeker.username == application.candidate.name:
                # Create notification with appropriate message based on status
                message = f"Your application for {application.job.job_title} has been updated to '{new_status}'."
                
                # Add more specific messages for different statuses
                if new_status == 'Interview Scheduled':
                    message = f"Good news! You've been selected for an interview for the {application.job.job_title} position at {application.job.company.name}."
                elif new_status == 'Shortlisted':
                    message = f"Congratulations! You've been shortlisted for the {application.job.job_title} position at {application.job.company.name}."
                elif new_status == 'Rejected':
                    message = f"Thank you for your interest in the {application.job.job_title} position at {application.job.company.name}. Unfortunately, we've decided to move forward with other candidates."
                elif new_status == 'Hired':
                    message = f"Congratulations! You've been selected for the {application.job.job_title} position at {application.job.company.name}."
                
                create_notification(
                    recipient=job_seeker,
                    message=message,
                    notification_type='application',
                    sender=request.user,
                    related_link=reverse('my_applications')
                )
                break
    except Exception as e:
        # Log the error but don't stop the status update
        print(f"Error creating notification: {str(e)}")
```

### New Application

```python
@login_required
def apply_to_job(request, job_id):
    # ... code to create application ...
    
    # Create notification for the recruiter
    create_notification(
        recipient=job.recruiter.user,
        message=f"New application received for {job.job_title} from {candidate.name}",
        notification_type='application',
        sender=request.user,
        related_link=reverse('view_job', args=[job.id])
    )
```

### Candidate Invitation

```python
@login_required
@require_POST
def invite_candidate(request):
    # ... code to process invitation ...
    
    # Create the notification message
    company_name = job.company.name
    job_title = job.job_title
    
    message = f"You've been invited to apply for the {job_title} position at {company_name}."
    if note:
        message += f" Recruiter's note: {note}"
    
    # Create the notification
    related_link = f"/jobs/{job_id}/apply/"
    notification = create_notification(
        recipient=job_seeker,
        sender=request.user,
        message=message,
        notification_type='job',
        related_link=related_link
    )
```

## Try It Yourself: Notification Flow

Let's practice tracing the notification flow:

1. An event occurs that triggers a notification (e.g., application status update)
2. The `create_notification` function is called with appropriate parameters
3. A new `Notification` record is created in the database
4. The context processor adds unread notification count to all templates
5. The notification appears in the dropdown in the navigation bar
6. The user clicks the notification
7. The `mark_notification_read` view marks the notification as read
8. The user is redirected to the related page

Try to identify the functions and templates involved in each step of this flow.

## Next Steps

In the next section, we'll explore the form handling and validation system, which ensures data integrity and provides a good user experience.
