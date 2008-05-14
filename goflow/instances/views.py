#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from goflow.workflow.api import getWorkItems, activateWorkitem, getInstance, forwardWorkItem, startInstance, getWorkItem, startSubflow
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from models import Instance

from goflow.workflow.decorators import login_required

@login_required
def mywork(request, template):
    me = request.user
    workitems = getWorkItems(user=me, notstatus='c', noauto=True)
    return render_to_response(template, {'user':me, 'workitems':workitems})

@login_required
def otherswork(request, template):
    worker = request.GET['worker']
    workitems = getWorkItems(username=worker, notstatus='c', noauto=False)
    return render_to_response(template, {'worker':worker, 'workitems':workitems})

@login_required
def instancehistory(request, template):
    id = int(request.GET['id'])
    inst = getInstance(id=id)
    return render_to_response(template, {'instance':inst})

@login_required
def myrequests(request, template):
    inst_list = Instance.objects.filter(user=request.user)
    return render_to_response(template, {'user':request.user, 'instances':inst_list})

@login_required
def activate(request):
    id = int(request.GET['workitem_id'])
    workitem = getWorkItem(id=id, user=request.user)
    activateWorkitem(workitem, request.user)
    return _app_response(workitem)

@login_required
def complete(request):
    id = int(request.GET['workitem_id'])
    workitem = getWorkItem(id=id, user=request.user)
    return _app_response(workitem)

def _app_response(workitem):
    id = workitem.id
    activity = workitem.activity
    if not activity.process.enabled:
        return HttpResponse('process %s disabled.' % activity.process.title)
    
    
    if activity.kind == 'f':
        # subflow
        sub_workitem = startSubflow(workitem, workitem.user)
        return _app_response(sub_workitem)
    
    # no application: default_app
    if not activity.application:
        url = '../../default_app'
        return HttpResponseRedirect('%s?workitem_id=%d' % (url, id))
    
    if activity.kind == 's':
        # standard activity
        return HttpResponseRedirect(activity.application.get_app_url(workitem))
    return HttpResponse('completion page.')

