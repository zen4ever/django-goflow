from django.template import Library
from goflow.runtime.models import WorkItem
register = Library()

def mywork(user):
    workitems = WorkItem.objects.list_safe(user=user, noauto=True)
    return {'workitems':workitems}
mywork = register.inclusion_tag("goflow/workitems.html")(mywork)

