from django import template

register = template.Library()

@register.filter
def filename(value):
    """Extract filename from a file path"""
    if value:
        return value.name.split('/')[-1]
    return ""

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a variable key"""
    if dictionary is None:
        return None
    return dictionary.get(key)
