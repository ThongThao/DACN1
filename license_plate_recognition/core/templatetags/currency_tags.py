from django import template

register = template.Library()

@register.filter
def format_vnd(value):
    try:
        return f"{float(value):,.0f} VND"
    except (ValueError, TypeError):
        return value