#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from api import forwardWorkItem
from models import Process, Activity, Transition, Application
from django.conf import settings
from django.contrib.auth.models import Group

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse

from goflow.instances.models import DefaultAppModel
from forms import ContentTypeForm
from django.contrib.contenttypes.models import ContentType
from api import startInstance

def index(request, template):
    """workflow dashboard handler.
    
    template context contains following objects:
    user, processes, roles, obinstances.
    """
    me = request.user
    roles = Group.objects.all()
    processes = Process.objects.all()
    obinstances = DefaultAppModel.objects.all()

    return render_to_response(template, {'user':me,
                                         'processes':processes,
                                         'roles':roles,
                                         'obinstances':obinstances})

def debug_switch_user(request, username, password, redirect=None):
    """fast user switch for test purpose.
    
    see template tag switch_users.
    """
    logout(request)
    #return HttpResponseRedirect(redirect)
    if not redirect:
        redirect = request.META['HTTP_REFERER']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(redirect)
        else:
            return HttpResponse('user is not active')
    else:
        return HttpResponse('authentication failed')

def userlist(request, template):
    return HttpResponse('user page.')


def process_dot(request, id, template):
    """graphviz generator (WIP).
    
    id process id
    template graphviz template
    
    context provides: process, roles, activities
    """
    process = Process.objects.get(id=int(id))
    context = {
               'process':process,
               'roles':({'name':'role1', 'color':'red'},),
               'activities':Activity.objects.filter(process=process)
               }
    return render_to_response(template, context)

def cron(request=None):
    """WIP
    """
    for t in Transition.objects.filter(condition__contains='workitem.time_out'):
        workitems = WorkItem.objects.filter(activity=t.input).exclude(status='c')
        for wi in workitems:
            forwardWorkItem(wi, timeoutForwarding=True)
    
    if request:
        request.user.message_set.create(message="cron has run.")
        if request.META.has_key('HTTP_REFERER'):
            url = request.META['HTTP_REFERER']
        else:
            url = 'home/'
        return HttpResponseRedirect(url)


def app_env(request, action, id, template=None):
    """creates/removes unit test environment for applications.
    
    a process named "test_[app]" with one activity
    a group with appropriate permission
    """
    app = Application.objects.get(id=int(id))
    rep = 'Nothing done.'
    if action == 'create':
        app.create_test_env(user=request.user)
        rep = 'test env created for app %s' % app.url
    if action == 'remove':
        app.remove_test_env()
        rep = 'test env removed for app %s' % app.url
    return HttpResponse(rep)

def test_start(request, id, template='test_start.html'):
    """starts test instances.
    
    for a given application, with its unit test environment, the user
    choose a content-type then generates unit test process instances
    by cloning existing content-type objects WIP.
    """
    app = Application.objects.get(id=int(id))
    context = {}
    if request.method == 'POST':
        submit_value = request.POST['action']
        if submit_value == 'Create':
            ctype = ContentType.objects.get(id=int(request.POST['ctype']))
            model = ctype.model_class()
            for inst in model.objects.all():
                inst.id = None
                startInstance(processName='test_%s' % app.url,
                              user=request.user, item=inst, title="%s test instance for app %s" % (ctype.name, app.url))
            request.user.message_set.create(message='test instances created')
        return HttpResponseRedirect('../..')
    form = ContentTypeForm()
    context['form'] = form
    return render_to_response(template, context)
