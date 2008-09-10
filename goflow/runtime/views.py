#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from models import ProcessInstance, WorkItem

from django.contrib.auth.decorators import login_required


@login_required
def mywork(request, template='goflow/mywork.html'):
    '''
    displays the worklist of the current user.
    
    parameters:
    
    template
        default:'goflow/mywork.html'
    '''
    workitems = WorkItem.objects.list_safe(user=request.user, noauto=True)
    return render_to_response(template, {'workitems':workitems},
                              context_instance=RequestContext(request))

@login_required
def otherswork(request, template='goflow/otherswork.html'):
    worker = request.GET['worker']
    workitems = WorkItem.objects.list_safe(username=worker, noauto=False)
    return render_to_response(template, {'worker':worker, 'workitems':workitems},
                              context_instance=RequestContext(request))

@login_required
def instancehistory(request, template='goflow/instancehistory.html'):
    id = int(request.GET['id'])
    inst = ProcessInstance.objects.get(pk=id)
    return render_to_response(template, {'instance':inst},
                              context_instance=RequestContext(request))

@login_required
def myrequests(request, template='goflow/myrequests.html'):
    inst_list = ProcessInstance.objects.filter(user=request.user)
    return render_to_response(template, {'instances':inst_list},
                              context_instance=RequestContext(request))

@login_required
def activate(request, id):
    '''
    activates and redirect to the application.
    
    parameters:
    
    id
        workitem id
    '''
    id = int(id)
    workitem = WorkItem.objects.get_safe(id=id, user=request.user)
    workitem.activate(request.user)
    return _app_response(workitem)

@login_required
def complete(request, id):
    '''
    redirect to the application.
    
    parameters:
    
    id
        workitem id
    '''
    id = int(id)
    workitem = WorkItem.objects.get_safe(id=id, user=request.user)
    return _app_response(workitem)

def _app_response(workitem):
    id = workitem.id
    activity = workitem.activity
    if not activity.process.enabled:
        return HttpResponse('process %s disabled.' % activity.process.title)
    
    
    if activity.kind == 'subflow':
        # subflow
        sub_workitem = workitem.start_subflow()
        return _app_response(sub_workitem)
    
    # no application: default_app
    if not activity.application:
        url = '../../../default_app'
        return HttpResponseRedirect('%s/%d/' % (url, id))
    
    if activity.kind == 'standard':
        # standard activity
        return HttpResponseRedirect(activity.application.get_app_url(workitem))
    return HttpResponse('completion page.')

