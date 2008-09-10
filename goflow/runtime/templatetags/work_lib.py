from django.template import Library
from goflow.runtime.models import WorkItem
register = Library()

def mywork(user):
    '''
    Display the worklist of a user as a table.

    The template *goflow/workitems.html* is used for rendering.

    Usage::

        {% mywork user %}
    
    settings required::

        MIDDLEWARE_CLASSES = (
            'django.middleware.common.CommonMiddleware',
            ...
        )

    **Tip**

    this can be used instead, if *workitems* variable is available
    in the context::

        {% include "goflow/workitems.html" %}
    
    when using *render_to_response* shortcut, don't forget
    to add a *RequestContext* as following::

        def some_view(request):
        # ...
        return render_to_response('my_template.html',
                                  my_data_dictionary,
                                  context_instance=RequestContext(request))
    '''
    workitems = WorkItem.objects.list_safe(user=user, noauto=True)
    return {'workitems':workitems}
mywork = register.inclusion_tag("goflow/workitems.html")(mywork)

