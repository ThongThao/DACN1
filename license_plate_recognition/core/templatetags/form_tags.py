from django import template

register = template.Library()

@register.filter(name='add_error_class')
def add_error_class(field, form_field):
    css_class = field.field.widget.attrs.get('class', '')
    if form_field.errors:
        return field.as_widget(attrs={"class": f"{css_class} is-invalid"})
    return field.as_widget(attrs={"class": css_class})
