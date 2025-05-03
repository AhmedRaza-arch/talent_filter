from django import forms
from django.utils.safestring import mark_safe

class TagInputWidget(forms.TextInput):
    """
    A custom widget that renders a text input with tag functionality.
    """
    template_name = 'widgets/tag_input.html'
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'input tag-input', 'placeholder': 'Type a skill and press Enter'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if value and isinstance(value, list):
            # Convert list to comma-separated string
            value = ', '.join(value)
        
        # Render the standard input
        input_html = super().render(name, value, attrs, renderer)
        
        # Add container for tags and hidden input for actual form submission
        html = f"""
        <div class="tag-input-container">
            {input_html}
            <div class="tags-container mt-2"></div>
            <input type="hidden" name="{name}" id="{attrs.get('id', name)}_hidden" value="{value or ''}">
        </div>
        """
        return mark_safe(html)
