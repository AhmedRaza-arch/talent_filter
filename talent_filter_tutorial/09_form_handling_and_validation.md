# 9. Form Handling and Validation

## Understanding Form Handling in Talent Filter

In this section, we'll explore how Talent Filter handles forms, validates user input, and processes form submissions. Forms are a critical part of the application, allowing users to register, create profiles, post jobs, and apply for positions.

## Django Forms Overview

Talent Filter uses Django's form system, which provides:

1. HTML form generation
2. Input validation
3. Error handling
4. Form processing

Django forms are defined as Python classes that specify the fields, validation rules, and processing logic.

## Key Form Classes

The application includes several custom form classes:

### Authentication Forms

```python
class UserLoginForm(AuthenticationForm):
    """Custom login form with styling"""
    
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class RecruiterSignUpForm(UserCreationForm):
    """Form for recruiter registration"""
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super(RecruiterSignUpForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
    
    def save(self, commit=True):
        user = super(RecruiterSignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create a minimal profile - details will be filled in later in settings
            recruiter_profile = RecruiterProfile.objects.create(
                user=user,
                role="" # Empty role that will be filled in settings
            )
            
            # Set user type
            user_type = user.usertype
            user_type.is_recruiter = True
            user_type.save()
        
        return user

class JobSeekerSignUpForm(UserCreationForm):
    """Form for job seeker registration"""
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super(JobSeekerSignUpForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
    
    def save(self, commit=True):
        user = super(JobSeekerSignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create a minimal profile - details will be filled in later
            job_seeker_profile = JobSeekerProfile.objects.create(
                user=user
            )
            
            # Set user type
            user_type = user.usertype
            user_type.is_job_seeker = True
            user_type.save()
        
        return user
```

### Profile Forms

```python
class UserProfileForm(forms.ModelForm):
    """Form for updating user information"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class JobSeekerProfileForm(forms.ModelForm):
    """Form for updating job seeker profile"""
    class Meta:
        model = JobSeekerProfile
        fields = ('skills', 'experience_years', 'education', 'location')
        widgets = {
            'skills': forms.TextInput(attrs={'class': 'input'}),
            'experience_years': forms.NumberInput(attrs={'class': 'input', 'step': '0.5'}),
            'education': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'input'}),
        }

class RecruiterProfileForm(forms.ModelForm):
    """Form for updating recruiter profile"""
    class Meta:
        model = RecruiterProfile
        fields = ('role', 'company_name', 'company_website')
        widgets = {
            'role': forms.TextInput(attrs={'class': 'input'}),
            'company_name': forms.TextInput(attrs={'class': 'input'}),
            'company_website': forms.URLInput(attrs={'class': 'input'}),
        }
```

### Job Form

```python
class JobForm(forms.ModelForm):
    """Form for creating and editing jobs"""
    # Company and location fields (not directly in the Job model)
    company_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'input'}))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'input'}))
    country = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'input'}))
    
    # Fields for JSON data
    key_responsibilities = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
        help_text="Enter each responsibility on a new line"
    )
    requirements = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
        help_text="Enter each requirement on a new line"
    )
    nice_to_have = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
        required=False,
        help_text="Enter each nice-to-have on a new line (optional)"
    )
    skills_required = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input', 'id': 'skills-input'}),
        help_text="Enter skills separated by commas"
    )
    external_portals = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 2}),
        required=False,
        help_text="Enter each external portal on a new line (optional)"
    )
    
    class Meta:
        model = Job
        fields = [
            'job_title', 'workplace_type', 'employment_type', 'experience_required',
            'application_deadline', 'summary', 'application_link', 'how_to_apply',
            'recruiter_name', 'recruiter_position', 'recruiter_email', 'recruiter_linkedin',
            'status', 'open_positions'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'input'}),
            'workplace_type': forms.Select(attrs={'class': 'select'}),
            'employment_type': forms.Select(attrs={'class': 'select'}),
            'experience_required': forms.TextInput(attrs={'class': 'input'}),
            'application_deadline': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'summary': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
            'application_link': forms.URLInput(attrs={'class': 'input'}),
            'how_to_apply': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'recruiter_name': forms.TextInput(attrs={'class': 'input'}),
            'recruiter_position': forms.TextInput(attrs={'class': 'input'}),
            'recruiter_email': forms.EmailInput(attrs={'class': 'input'}),
            'recruiter_linkedin': forms.URLInput(attrs={'class': 'input', 'required': False}),
            'status': forms.Select(attrs={'class': 'select'}),
            'open_positions': forms.NumberInput(attrs={'class': 'input', 'min': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(JobForm, self).__init__(*args, **kwargs)
        
        # If we're editing an existing job
        if self.instance.pk:
            # Set initial values for company and location fields
            if hasattr(self.instance, 'company') and self.instance.company:
                self.fields['company_name'].initial = self.instance.company.name
                if hasattr(self.instance.company, 'location') and self.instance.company.location:
                    self.fields['city'].initial = self.instance.company.location.city
                    self.fields['state'].initial = self.instance.company.location.state
                    self.fields['country'].initial = self.instance.company.location.country
            
            # Set initial values for JSON fields
            self.fields['key_responsibilities'].initial = '\n'.join(self.instance.get_key_responsibilities())
            self.fields['requirements'].initial = '\n'.join(self.instance.get_requirements())
            self.fields['nice_to_have'].initial = '\n'.join(self.instance.get_nice_to_have())
            self.fields['skills_required'].initial = ', '.join(self.instance.get_skills_required())
            self.fields['external_portals'].initial = '\n'.join(self.instance.get_external_portals())
        
        # If user is provided, pre-fill recruiter information
        if self.user and not self.instance.pk:
            self.fields['recruiter_name'].initial = self.user.get_full_name() or self.user.username
            if hasattr(self.user, 'recruiterprofile'):
                self.fields['recruiter_position'].initial = self.user.recruiterprofile.role
                self.fields['company_name'].initial = self.user.recruiterprofile.company_name
                self.fields['recruiter_email'].initial = self.user.email
    
    def clean(self):
        cleaned_data = super(JobForm, self).clean()
        
        # Convert newline-separated text to lists for JSON fields
        for field_name in ['key_responsibilities', 'requirements', 'nice_to_have', 'external_portals']:
            if field_name in cleaned_data and cleaned_data[field_name]:
                # Split by newline and remove empty lines
                items = [item.strip() for item in cleaned_data[field_name].split('\n') if item.strip()]
                cleaned_data[field_name] = items
        
        # Convert comma-separated skills to a list
        if 'skills_required' in cleaned_data and cleaned_data['skills_required']:
            # Split by comma and remove empty items
            skills = [skill.strip() for skill in cleaned_data['skills_required'].split(',') if skill.strip()]
            cleaned_data['skills_required'] = skills
        
        return cleaned_data
    
    def save(self, commit=True):
        job = super(JobForm, self).save(commit=False)
        
        # Create or get location
        location, _ = Location.objects.get_or_create(
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            country=self.cleaned_data['country']
        )
        
        # Create or get company
        company, _ = Company.objects.get_or_create(
            name=self.cleaned_data['company_name'],
            defaults={'location': location}
        )
        
        # Set company for the job
        job.company = company
        
        # Set recruiter information
        if self.user and hasattr(self.user, 'recruiterprofile'):
            job.recruiter = self.user.recruiterprofile
        
        # Set JSON fields
        job.set_key_responsibilities(self.cleaned_data['key_responsibilities'])
        job.set_requirements(self.cleaned_data['requirements'])
        if 'nice_to_have' in self.cleaned_data and self.cleaned_data['nice_to_have']:
            job.set_nice_to_have(self.cleaned_data['nice_to_have'])
        job.set_skills_required(self.cleaned_data['skills_required'])
        if 'external_portals' in self.cleaned_data and self.cleaned_data['external_portals']:
            job.set_external_portals(self.cleaned_data['external_portals'])
        
        if commit:
            job.save()
        
        return job
```

## Form Rendering in Templates

Forms are rendered in templates using Django's form rendering capabilities:

### Basic Form Rendering

```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="button is-primary">Submit</button>
</form>
```

### Custom Form Rendering

```html
<form method="post">
    {% csrf_token %}
    <div class="field">
        <label class="label">{{ form.username.label }}</label>
        <div class="control">
            {{ form.username }}
        </div>
        {% if form.username.errors %}
        <p class="help is-danger">{{ form.username.errors.0 }}</p>
        {% endif %}
    </div>
    
    <div class="field">
        <label class="label">{{ form.email.label }}</label>
        <div class="control">
            {{ form.email }}
        </div>
        {% if form.email.errors %}
        <p class="help is-danger">{{ form.email.errors.0 }}</p>
        {% endif %}
    </div>
    
    <div class="field">
        <label class="label">{{ form.password1.label }}</label>
        <div class="control">
            {{ form.password1 }}
        </div>
        {% if form.password1.errors %}
        <p class="help is-danger">{{ form.password1.errors.0 }}</p>
        {% endif %}
    </div>
    
    <div class="field">
        <label class="label">{{ form.password2.label }}</label>
        <div class="control">
            {{ form.password2 }}
        </div>
        {% if form.password2.errors %}
        <p class="help is-danger">{{ form.password2.errors.0 }}</p>
        {% endif %}
    </div>
    
    <div class="field">
        <div class="control">
            <button type="submit" class="button is-primary is-fullwidth">Register</button>
        </div>
    </div>
</form>
```

## Form Processing in Views

Forms are processed in view functions:

### Basic Form Processing

```python
def job_seeker_signup(request):
    if request.method == 'POST':
        form = JobSeekerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Please complete your profile to continue.")
            return redirect('job_seeker_profile')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = JobSeekerSignUpForm()
    return render(request, 'job_seeker_signup.html', {'form': form})
```

### Form Processing with File Uploads

```python
@login_required
def job_seeker_profile(request):
    # ... code to check user type ...
    
    # Get or create job seeker profile
    job_seeker_profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    
    # Initialize forms
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'user_profile':
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Personal information updated successfully!")
                return redirect('job_seeker_profile')
        
        elif form_type == 'job_seeker_profile':
            # Check if this is the upload form or the professional info form
            is_upload_form = 'upload-form' in request.POST.get('form_id', '')
            
            if is_upload_form:
                # Handle file uploads directly
                if 'profile_picture' in request.FILES:
                    job_seeker_profile.profile_picture = request.FILES['profile_picture']
                    print(f"Uploaded profile picture: {job_seeker_profile.profile_picture.name}")
                
                if 'resume' in request.FILES:
                    job_seeker_profile.resume = request.FILES['resume']
                    print(f"Uploaded resume: {job_seeker_profile.resume.name}")
                    # Suggest using AI extraction
                    messages.info(request, "Resume uploaded! Use the 'Extract Data with AI' button to automatically fill your profile.")
                
                job_seeker_profile.save()
                messages.success(request, "Files uploaded successfully!")
            else:
                # Handle professional info update (excluding file fields)
                profile_form = JobSeekerProfileForm(request.POST, instance=job_seeker_profile)
                if profile_form.is_valid():
                    profile = profile_form.save(commit=False)
                    # Don't touch the file fields
                    profile.save()
                    messages.success(request, "Professional information updated successfully!")
            
            return redirect('job_seeker_profile')
        
        elif form_type == 'password_change':
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Password changed successfully!")
                return redirect('job_seeker_profile')
        
        # If we get here, there was an error in the form submission
        # We'll recreate the appropriate form with errors below
    else:
        # Initialize all forms with current data
        user_form = UserProfileForm(instance=request.user)
        profile_form = JobSeekerProfileForm(instance=job_seeker_profile)
        password_form = CustomPasswordChangeForm(request.user)
    
    # ... code to handle form errors ...
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'profile_completion': profile_completion,
        'job_seeker_profile': job_seeker_profile,
        'is_new_profile': is_new_profile,
    }
    
    return render(request, 'job_seeker_profile.html', context)
```

## Custom Form Widgets

The application includes custom form widgets for enhanced functionality:

```python
class TagInput(forms.TextInput):
    """Custom widget for tag-based input"""
    template_name = 'widgets/tag_input.html'
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'input tag-input'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['type'] = 'hidden'
        if value:
            context['tags'] = value.split(',')
        else:
            context['tags'] = []
        return context
```

The widget template:

```html
<!-- widgets/tag_input.html -->
<div class="tag-input-container">
    <input type="{{ widget.type }}" name="{{ widget.name }}" {% if widget.value != None %}value="{{ widget.value }}"{% endif %} {% include "django/forms/widgets/attrs.html" %}>
    <div class="tag-input-field">
        <div class="tags-container">
            {% for tag in tags %}
            <span class="tag is-primary">
                {{ tag }}
                <button type="button" class="delete is-small"></button>
            </span>
            {% endfor %}
        </div>
        <input type="text" class="tag-input-field-input" placeholder="Type and press Enter to add">
    </div>
</div>
```

## Form Validation

Forms include validation to ensure data integrity:

### Built-in Validation

Django provides built-in validation for common field types:

- `EmailField`: Ensures valid email format
- `URLField`: Ensures valid URL format
- `IntegerField`: Ensures numeric input
- `DateField`: Ensures valid date format

### Custom Validation

Custom validation can be added using the `clean_<fieldname>` method:

```python
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise forms.ValidationError("This email is already in use.")
    return email
```

Or by overriding the `clean` method for cross-field validation:

```python
def clean(self):
    cleaned_data = super().clean()
    password1 = cleaned_data.get('password1')
    password2 = cleaned_data.get('password2')
    
    if password1 and password2 and password1 != password2:
        self.add_error('password2', "The two password fields didn't match.")
    
    return cleaned_data
```

## Form Styling

Forms are styled using the Bulma CSS framework:

```python
def __init__(self, *args, **kwargs):
    super(UserLoginForm, self).__init__(*args, **kwargs)
    for field_name, field in self.fields.items():
        field.widget.attrs.update({'class': 'input'})
```

This adds the `input` class to all form fields, which applies Bulma's styling.

## JavaScript Enhancements

Forms are enhanced with JavaScript for better user experience:

### Tag Input

```javascript
// Tag input functionality
$(document).ready(function() {
    // Add tag when Enter is pressed
    $('.tag-input-field-input').keydown(function(e) {
        if (e.keyCode === 13) {  // Enter key
            e.preventDefault();
            
            var tag = $(this).val().trim();
            if (tag) {
                // Add the tag
                var tagElement = $('<span class="tag is-primary">' + tag + '<button type="button" class="delete is-small"></button></span>');
                $(this).closest('.tag-input-field').find('.tags-container').append(tagElement);
                
                // Clear the input
                $(this).val('');
                
                // Update the hidden input
                updateTagsInput($(this).closest('.tag-input-container'));
            }
        }
    });
    
    // Remove tag when delete button is clicked
    $(document).on('click', '.tag .delete', function() {
        $(this).parent().remove();
        updateTagsInput($(this).closest('.tag-input-container'));
    });
    
    // Update the hidden input with all tags
    function updateTagsInput(container) {
        var tags = [];
        container.find('.tag').each(function() {
            tags.push($(this).text().trim());
        });
        container.find('input[type="hidden"]').val(tags.join(','));
    }
});
```

### File Upload Preview

```javascript
// Show preview of uploaded image
$('#profile-picture-input').change(function() {
    if (this.files && this.files[0]) {
        var reader = new FileReader();
        
        reader.onload = function(e) {
            $('#profile-picture-preview').attr('src', e.target.result);
            $('#profile-picture-preview-container').removeClass('is-hidden');
        }
        
        reader.readAsDataURL(this.files[0]);
    }
});
```

## Try It Yourself: Form Processing Flow

Let's practice tracing the form processing flow:

1. User loads a page with a form (e.g., job creation form)
2. The view function initializes the form with initial data
3. The form is rendered in the template
4. User fills out the form and submits it
5. The view function processes the form data
6. If the form is valid, the data is saved and the user is redirected
7. If the form is invalid, the form is re-rendered with error messages

Try to identify the functions and templates involved in each step of this flow.

## Next Steps

In the next section, we'll explore the UI/UX implementation, including the use of the Bulma CSS framework and custom styling.
