from django import template

register = template.Library()

@register.filter
def percentage(value, total):
    """
    Calculate the percentage of a value relative to a total.
    
    Usage: {{ value|percentage:total }}
    """
    if total == 0:
        return 0
    
    try:
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_range(value, arg):
    """
    Generate a range of numbers from value to arg.
    
    Usage: {% for i in start|get_range:end %}
    """
    try:
        start = int(value)
        end = int(arg)
        return range(start, end + 1)
    except (ValueError, TypeError):
        return range(0) 