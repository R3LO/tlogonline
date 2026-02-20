from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary by key
    Usage: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return {}
    return dictionary.get(key, {})


@register.filter
def get_modes(bands_dict, band_key):
    """
    Get modes dictionary for a specific band
    Usage: {{ bands|get_modes:"17M" }}
    """
    if bands_dict is None:
        return {}
    return bands_dict.get(band_key, {})


@register.filter
def startswith(text, prefix):
    """
    Check if text starts with prefix
    Usage: {% if text|startswith:"SAT:" %}
    """
    if text is None:
        return False
    return str(text).startswith(prefix)
