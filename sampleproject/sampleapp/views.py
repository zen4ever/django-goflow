# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response

from goflow.workflow.api import get_workitems
from goflow.workflow.decorators import login_required

@login_required
def home(request, template='sample/home.html'):
    me = request.user
    workitems = get_workitems(user=me, noauto=True)
    return render_to_response(template, {'user':me,
                                         'workitems':workitems,
                                         })

def myview(request):
    return HttpResponse('My view')
