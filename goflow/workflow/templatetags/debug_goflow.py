from django.template import Library
from django.conf import settings

register = Library()

@register.simple_tag
def switch_users():
    """
    Returns a menu to switch users quickly.

    Settings required::

        settings.TEST_USERS = (('user1', 'pass1'), ...)
        settings.DEBUG = True

    FOR TESTING PURPOSE ONLY
    """
    if not settings.DEBUG: return ''
    try:
        if settings.TEST_USERS:
            pass
    except Exception:
        return ''
    
    content = 'switch user:'
    for item in settings.TEST_USERS:
        u, p = item
        content += ' [<a href=switch/%s/%s/>%s</a>]' % (u,p,u)
    return content
