from django.template import Library
#from django.conf import settings
from goflow.apptools.models import ImageButton

register = Library()


def _get_transitions_out_images(activity):
    if activity.split_mode == 'and':
        raise Exception('_get_transitions_out_images: xor split_mode required')
    transitions = Transition.objects.filter(input=activity)
    icons = []
    for t in transitions:
        if t.icon: icons.append(t.icon)


def input_buttons(context):
    sub_context ={'submit_name':context['submit_name']}
    if context.has_key('ok_values'): sub_context['ok_values'] = context['ok_values']
    if context.has_key('save_value'): sub_context['save_value'] = context['save_value']
    if context.has_key('cancel_value'): sub_context['cancel_value'] = context['cancel_value']
    return sub_context
input_buttons = register.inclusion_tag("goflow/apptools/input_buttons.html", takes_context=True)(input_buttons)

@register.simple_tag
def image_button(action):
    return ImageButton.objects.get(action=action).graphic_input()
