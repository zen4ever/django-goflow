# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from goflow.runtime.models import WorkItem
from django.contrib.auth.decorators import login_required
from django.conf import settings

@login_required
def home(request, template='sample/home.html'):
    local_code = request.LANGUAGE_CODE or settings.LANGUAGE_CODE
    local_template = '%s/%s' % (local_code, template)
    workitems = WorkItem.objects.list_safe(user=request.user, noauto=True)
    return render_to_response((local_template, template), {'workitems':workitems},
                              context_instance=RequestContext(request))

def myview(request):
    return HttpResponse('My view')

