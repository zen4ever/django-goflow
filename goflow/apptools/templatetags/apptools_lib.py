from django.template import Library
#from django.conf import settings
from goflow.apptools.models import ImageButton

register = Library()

def form_ext(form):
    '''
    This will insert a form, in a bit more sophisticated way than {{ form }}.

    Required and optional fields are displayed differently. For details,
    see template file *goflow/apptools/edit_form.html*.

    parameter:

    form
        form variable

    Usage::

        {% form_ext form %}
    
    the current implementation is equivalent to::

        {% include "goflow/apptools/edit_form.html" %}
    '''
    return {'form':form}
form_ext = register.inclusion_tag("goflow/apptools/edit_form.html")(form_ext)

def _get_transitions_out_images(activity):
    if activity.split_mode == 'and':
        raise Exception('_get_transitions_out_images: xor split_mode required')
    transitions = Transition.objects.filter(input=activity)
    icons = []
    for t in transitions:
        if t.icon: icons.append(t.icon)


def input_buttons(context):
    '''
    This will insert submit buttons in application templates.

    The template *goflow/apptools/input_buttons.html* is used for rendering.

    Usage::

        {% input_buttons %}

    - *Context requirements*

    submit_name
        name of the buttons
    ok_values
        sequence of values, used for button value generation
    cancel_value
        value for the *cancel* button

    - *Context options*

    save_value
        can be used with the *edit_model* application: this button
        saves the object but does not complete the task.
    '''
    sub_context ={'submit_name':context['submit_name']}
    if context.has_key('ok_values'): sub_context['ok_values'] = context['ok_values']
    if context.has_key('save_value'): sub_context['save_value'] = context['save_value']
    if context.has_key('cancel_value'): sub_context['cancel_value'] = context['cancel_value']
    return sub_context
input_buttons = register.inclusion_tag("goflow/apptools/input_buttons.html", takes_context=True)(input_buttons)

@register.simple_tag
def image_button(action):
    '''
    This will insert submit image buttons in application templates.
    
    Usage::

        {% for value in ok_values %}
            {% image_button value %}
        {% endfor %}
        
        {% image_button cancel_value %}

    ok_values
        sequence of actions corresponding to transition conditions.
        Example: when the image button with the *edit* action is pressed,
        the transition such as *transition.condition = 'edit'* will be
        cadidate for workitem forwarding.

    cancel_value
        action correponding to cancel.
    
    An *action* (like *edit*, *new*, *exit*, ...) is a "slug" mapped to
    an image, or more exactly an *Icon* model; this mapping is implemented
    with *ImageButton* model.
    '''
    return ImageButton.objects.get(action=action).graphic_input()
