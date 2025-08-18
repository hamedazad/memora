from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup dictionary values by key"""
    if dictionary is None:
        return None
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None

@register.filter
def get_item(dictionary, key):
    """Template filter to get dictionary item by key"""
    if dictionary is None:
        return None
    try:
        if hasattr(dictionary, 'get'):
            return dictionary.get(key)
        elif hasattr(dictionary, '__getitem__'):
            return dictionary[key]
        else:
            return None
    except (KeyError, TypeError, AttributeError):
        return None


