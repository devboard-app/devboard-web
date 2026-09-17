from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def field_errors(errors, field):
    """Render a Bootstrap invalid-feedback block for one field's messages.

    `errors` is the {"field": ["msg", ...]} dict a ServiceError carries.
    Reused by every form with more than a single top-level error banner
    (register, forgot/reset password, and later team/project/ticket forms).
    """
    if not errors:
        return ''
    messages = errors.get(field)
    if not messages:
        return ''
    return format_html('<div class="invalid-feedback d-block">{}</div>', '; '.join(messages))


@register.filter
def has_error(errors, field):
    return bool(errors and errors.get(field))
