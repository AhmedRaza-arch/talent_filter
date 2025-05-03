# 2. System Architecture

## Understanding the Big Picture

In this section, we'll explore how Talent Filter is structured and how its components work together. Understanding the architecture will help you navigate the codebase more effectively.

## Django MVT Architecture

Talent Filter follows Django's Model-View-Template (MVT) architecture, which is Django's variation of the more common Model-View-Controller (MVC) pattern:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Model    │     │    View     │     │  Template   │
│             │     │             │     │             │
│  (Data &    │◄───►│  (Business  │◄───►│   (HTML     │
│   Logic)    │     │   Logic)    │     │ Generation) │
└─────────────┘     └─────────────┘     └─────────────┘
        ▲                  ▲                   ▲
        │                  │                   │
        └──────────────────▼───────────────────┘
                           │
                    ┌─────────────┐
                    │    URLs     │
                    │  (Routing)  │
                    └─────────────┘
                           ▲
                           │
                    ┌─────────────┐
                    │   Client    │
                    │  (Browser)  │
                    └─────────────┘
```

- **Models** (`models.py`): Define the data structure and database schema
- **Views** (`views.py`): Handle HTTP requests, process data, and return responses
- **Templates** (HTML files): Define how data is presented to the user
- **URLs** (`urls.py`): Map URLs to view functions

## Project Structure

The Talent Filter project follows a standard Django project structure:

```
talent_filter/                  # Project root
├── Talent_Filter/              # Project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Project settings
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py
├── talent_filter_app/          # Main application
│   ├── __init__.py
│   ├── admin.py                # Admin interface configuration
│   ├── apps.py                 # App configuration
│   ├── async_utils.py          # Asynchronous processing utilities
│   ├── context_processors.py   # Template context processors
│   ├── extraction_status.py    # Resume extraction status tracking
│   ├── forms.py                # Form definitions
│   ├── migrations/             # Database migrations
│   ├── models.py               # Data models
│   ├── prompts.py              # AI prompt templates
│   ├── static/                 # Static files (CSS, JS, images)
│   ├── templates/              # HTML templates
│   ├── templatetags/           # Custom template tags
│   ├── tests.py                # Test cases
│   ├── urls.py                 # App URL configuration
│   ├── utils.py                # Utility functions
│   ├── views.py                # View functions
│   └── widgets.py              # Custom form widgets
├── manage.py                   # Django management script
├── media/                      # User-uploaded files
└── static/                     # Project-wide static files
```

## Key Components

Let's look at the key components of the Talent Filter application:

### 1. Models (`models.py`)

The models define the database schema and business logic. Key models include:

- **User-related models**: `UserType`, `RecruiterProfile`, `JobSeekerProfile`
- **Job-related models**: `Job`, `Company`, `Location`, `Application`
- **AI-related models**: `JobMatchAnalysis`, `CandidateRecommendation`
- **Communication models**: `Notification`

### 2. Views (`views.py`)

Views handle HTTP requests and return responses. They're organized by user type and functionality:

- **Authentication views**: Login, signup, logout
- **Recruiter views**: Dashboard, job management, candidate management
- **Job seeker views**: Profile, job search, applications
- **AI-related views**: Resume parsing, job matching

### 3. Templates

Templates define the HTML structure and presentation. They're organized by feature:

- Base templates (`base.html`, `base1.html`)
- Recruiter templates (`dashboard.html`, `job_listings.html`, etc.)
- Job seeker templates (`job_seeker_dashboard.html`, `available_jobs.html`, etc.)
- Shared templates (`login.html`, `notifications.html`, etc.)

### 4. Utility Modules

Several utility modules provide specialized functionality:

- **utils.py**: General utilities, AI integration, file handling
- **async_utils.py**: Asynchronous processing for long-running tasks
- **extraction_status.py**: Tracking resume extraction progress
- **prompts.py**: AI prompt templates for different extraction tasks

## Data Flow

Let's trace the data flow for a typical user interaction - a job seeker uploading a resume:

1. User uploads a resume through a form in `job_seeker_profile.html`
2. The form submits to the `job_seeker_profile` view in `views.py`
3. The view saves the file and redirects to the profile page
4. User clicks "Extract Data with AI"
5. This triggers the `extract_resume_data` view
6. The view starts a background thread that calls `extract_resume_data_from_api` in `utils.py`
7. This function reads the resume file and makes API calls to extract information
8. Extraction status is tracked in the cache using functions from `extraction_status.py`
9. The extracted data is saved to the `JobSeekerProfile` model
10. The UI is updated to show the extracted information

## External Integrations

Talent Filter integrates with external services:

- **Google Gemini API**: Used for AI-powered resume parsing and job matching
- **File Processing Libraries**: PyPDF2 and python-docx for reading resume files

## Try It Yourself: Tracing a Request

Let's practice tracing a request through the system:

1. Find the URL pattern for the job listings page in `urls.py`
2. Locate the corresponding view function in `views.py`
3. Identify which models the view interacts with
4. Find the template that renders the page
5. Look for any JavaScript that enhances the page functionality

## Next Steps

In the next section, we'll dive deeper into the database models, exploring how data is structured and relationships between different entities.
