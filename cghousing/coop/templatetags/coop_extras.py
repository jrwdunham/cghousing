from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def coop_user_name(user):
    if user is None:
        return u'the system'
    elif user.first_name:
        return u'%s %s' % (user.first_name, user.last_name)
    else:
        return user.username

@register.filter
@stringfilter
def form_row_class(field_name, errors_dict):
    if errors_dict.get(field_name):
        return "form-row field-%s errors" % field_name
    else:
        return "form-row field-%s" % field_name

