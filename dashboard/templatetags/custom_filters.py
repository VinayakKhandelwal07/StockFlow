from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if not isinstance(dictionary, dict):
        return None
    
    # Try exact key lookup first
    if key in dictionary:
        return dictionary[key]
    
    # Try int key lookup if possible
    try:
        int_key = int(key)
        if int_key in dictionary:
            return dictionary[int_key]
    except (ValueError, TypeError):
        pass
    
    # Try string key lookup (in case dictionary keys are strings)
    try:
        str_key = str(key)
        if str_key in dictionary:
            return dictionary[str_key]
    except (ValueError, TypeError):
        pass
    
    # If no key found, return 0 (default)
    return 0
