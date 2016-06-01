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

FILE_FA_ICONS = {
    'application/pdf': 'file-pdf-o',
    'image/gif': 'file-image-o',
    'image/png': 'file-image-o',
    'image/jpeg': 'file-image-o',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        'file-word-o',
    'application/msword': 'file-word-o',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        'file-excel-o',
    'application/ms-excel': 'file-excel-o',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        'file-powerpoint-o',
    'application/ms-powerpointtd': 'file-powerpoint-o',
    'audio/vorbis': 'file-audio-o',
    'application/ogg': 'file-audio-o',
    'audio/wav': 'file-audio-o',
    'audio/x-wav': 'file-audio-o',
    'audio/mpeg': 'file-audio-o',
}

FILE_HUMAN = {
    'application/pdf': 'PDF',
    'image/gif': 'image',
    'image/png': 'image',
    'image/jpeg': 'image',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        'word processing',
    'application/msword': 'word processing',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        'spreadsheet',
    'application/ms-excel': 'spreadsheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        'presentation',
    'application/ms-powerpointtd': 'presentation',
    'audio/vorbis': 'audio',
    'application/ogg': 'audio',
    'audio/wav': 'audio',
    'audio/x-wav': 'audio',
    'audio/mpeg': 'audio',
}

@register.filter
def mime2awesome(mime_type):
    return FILE_FA_ICONS.get(mime_type, 'file-o')

@register.filter
def mime2human(mime_type):
    return FILE_HUMAN.get(mime_type, 'file')

@register.filter
def addstr(arg1, arg2):
    """Concatenate arg1 & arg2.

    """

    return str(arg1) + str(arg2)

