from django.template import Library
from django.conf import settings

register = Library()

@register.simple_tag
def graphics_url_prefix():
    """Returns the string contained in the setting GRAPHICS_JS_URL.
    
    (obsolete since django 1.0 ?)
    
    A suitable value is *http://www.walterzorn.com/scripts/*
    """
    return settings.GRAPHICS_JS_URL
