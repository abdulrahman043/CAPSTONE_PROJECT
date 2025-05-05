# WasslPoint/main/templatetags/query_params.py

from django import template
from urllib.parse import urlencode

register = template.Library() # Important: Django looks for this variable

@register.simple_tag
def url_params(request, **kwargs):
    """
    Builds URL parameters, preserving existing ones from the request GET params,
    and overriding/adding specified kwargs. Removes keys with None or empty values.
    """
    updated = request.GET.copy()
    for key, value in kwargs.items():
        # Add/update the key if value is provided
        if value is not None and value != '':
            updated[key] = str(value) # Ensure value is string
        # Remove the key if the provided value is None/empty and the key exists
        elif key in updated:
             del updated[key]

    # Remove 'page' as it's handled separately by pagination links
    if 'page' in updated:
        del updated['page']

    # Return the encoded parameters prefixed with '&' if any exist
    if updated:
        # Use safe='' to prevent encoding of '&' and '='
        return '&' + urlencode(updated, safe='&=')
    return ''