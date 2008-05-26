#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from api import startInstance, getWorkItem, completeWorkitem, activateWorkitem, isProcessEnabled, check_start_instance_perm
from django.db import models
from django.contrib.auth.models import User
from django.newforms import form_for_model, form_for_instance

from django.contrib.auth.decorators import permission_required
# little hack
from decorators import login_required
from goflow.instances.models import DefaultAppModel
from goflow.instances.forms import DefaultAppForm

from django.contrib.admin.views.main import add_stage
from django.conf import settings

import logger, logging
_logger = logging.getLogger('workflow.log')


@login_required
def start_application(request, app_label=None, model_name=None, process_name=None, instance_label=None,
                       template=None, template_def='start_application.html',
                       form_class=None, redirect='home', submit_name='action',
                       ok_value='OK', cancel_value='Cancel'):
    '''
    generic handler for application that enters a workflow.
    
    parameters:
    
    app_label, model_name    model linked to workflow instance
    process_name             default: same name as app_label
    instance_label           default: process_name + str(object)
    template                 default: 'start_%s.html' % app_label
    template_def             used if template not found; default: 'start_application.html'
    form_class               default: old form_for_model
    '''
    if not process_name: process_name = app_label
    try:
        check_start_instance_perm(process_name, request.user)
    except Exception, v:
        return HttpResponse(str(v))
    
    #if not instance_label: instance_label = '%s-%s' % (app_label, model_name)
    if not template: template = 'start_%s.html' % app_label
    if not form_class:
        model = models.get_model(app_label, model_name)
        form_class = form_for_model(model)
        is_form_used = False
    else:
        is_form_used = True
    
    if request.method == 'POST':
        form = form_class(request.POST)
        submit_value = request.POST[submit_name]
        if submit_value == cancel_value:
            return HttpResponseRedirect(redirect)
        
        if submit_value == ok_value and form.is_valid():
            try:
                if is_form_used:
                    ob = form.save(user=request.user, data=request.POST)
                else:
                    ob = form.save()
            except Exception, v:
                if is_form_used:
                    raise
                    _logger.error("the save method of the form must accept parameters user and data")
                else:
                    _logger.error("forme save error: %s", str(v))
            
            if ob:
                startInstance(process_name, request.user, ob, instance_label)
            
            return HttpResponseRedirect(redirect)
    else:
        form = form_class()
        # precheck
        form.pre_check(user=request.user)
    context = {'form': form, 'process_name':process_name,
               'submit_name':submit_name, 'ok_value':ok_value, 'cancel_value':cancel_value}
    return render_to_response((template, template_def), context)


@login_required
def default_app(request, id, template='default_app.html', redirect='home', submit_name='action'):
    '''
    default application, used for prototyping workflows.
    '''
    submit_values = ('OK', 'Cancel')
    id = int(id)
    if request.method == 'POST':
        data = request.POST.copy()
        workitem = getWorkItem(id, user=request.user)
        inst = workitem.instance
        ob = inst.wfobject()
        form = DefaultAppForm(data, instance=ob)
        if form.is_valid():
            #data = form.cleaned_data
            submit_value = request.POST[submit_name]
            
            workitem.instance.condition = submit_value
            
            workitem.instance.save()
            ob = form.save(workitem=workitem, submit_value=submit_value)
            #ob.comment = data['comment']
            #ob.save(workitem=workitem, submit_value=submit_value)
            
            completeWorkitem(workitem, request.user)
            return HttpResponseRedirect(redirect)
    else:
        workitem = getWorkItem(id, user=request.user)
        inst = workitem.instance
        ob = inst.wfobject()
        form = DefaultAppForm(instance=ob)
        # add header with activity description, submit buttons dynamically
        if workitem.activity.splitMode == 'x':
            tlist = workitem.activity.transition_inputs.all()
            if tlist.count() > 0:
                submit_values = []
                for t in tlist:
                    submit_values.append( _cond_to_button_value(t.condition) )
    
    return render_to_response(template, {'form': form,
                                         'activity':workitem.activity,
                                         'workitem':workitem,
                                         'instance':inst,
                                         'history':inst.wfobject().history,
                                         'submit_values':submit_values,})


def _cond_to_button_value(cond):
    '''
    extract "a value" from "instance.condition=='a value'"
    used to generate buttons on default application
    '''
    import re
    s = cond.strip()
    try:
        m = re.match("instance.condition *== *(.*)", s)
        s = m.groups()[0]
        s = s.strip('"').strip("'")
    except Exception:
        pass
    return s


@login_required
def edit_model(request, id, form_class, cmp_attr=None,template=None, template_def='edit_model.html', title="",
               redirect='home', submit_name='action', ok_values=('OK',), save_value='Save', cancel_value='Cancel'):
    '''
    generic handler for editing a model
    '''
    if not template: template = 'edit_%s.html' % form_class._meta.model._meta.object_name.lower()
    model_class = form_class._meta.model
    workitem = getWorkItem(int(id), user=request.user)
    instance = workitem.instance
    activity = workitem.activity
    
    obj = instance.wfobject()
    obj_context = obj
    # objet composite intermédiaire
    if cmp_attr:
        obj = getattr(obj, cmp_attr)
    
    template = override_app_params(activity, 'template', template)
    redirect = override_app_params(activity, 'redirect', redirect)
    submit_name = override_app_params(activity, 'submit_name', submit_name)
    ok_values = override_app_params(activity, 'ok_values', ok_values)
    cancel_value = override_app_params(activity, 'cancel_value', cancel_value)

    if request.method == 'POST':
        form = form_class(request.POST, instance=obj)
        submit_value = request.POST[submit_name]
        if submit_value == cancel_value:
            return HttpResponseRedirect(redirect)
        
        if form.is_valid():
            if (submit_value == save_value):
                # just save
                ob = form.save()
                try:
                    ob = form.save(workitem=workitem, submit_value=submit_value)
                except Exception, v:
                    raise Exception("the save method of the form must accept parameters workitem and submit_value")
                return HttpResponseRedirect(redirect)
            
            if submit_value in ok_values:
                # save and complete activity
                ob = form.save()
                try:
                    ob = form.save(workitem=workitem, submit_value=submit_value)
                except Exception, v:
                    raise Exception("the save method of the form must accept parameters workitem and submit_value")
                instance.condition = submit_value
                instance.save()
                completeWorkitem(workitem, request.user)
                return HttpResponseRedirect(redirect)
    else:
        form = form_class(instance=obj)
        # precheck
        form.pre_check(obj_context, user=request.user)
    return render_to_response((template, template_def), {'form': form,
                                                         'object':obj,
                                                         'object_context':obj_context,
                                                         'instance':instance,
                                                         'submit_name':submit_name,
                                                         'ok_values':ok_values,
                                                         'save_value':save_value,
                                                         'cancel_value':cancel_value,
                                                         'title':title,})


@login_required
def view_application(request, id, template='view_application.html', redirect='home', title="",
               submit_name='action', ok_values=('OK',), cancel_value='Cancel'):
    '''
    generic handler for a view.
    
    useful for a simple view or a complex object edition.
    '''
    workitem = getWorkItem(int(id), user=request.user)
    instance = workitem.instance
    activity = workitem.activity
    
    obj = instance.wfobject()
    
    template = override_app_params(activity, 'template', template)
    redirect = override_app_params(activity, 'redirect', redirect)
    submit_name = override_app_params(activity, 'submit_name', submit_name)
    ok_values = override_app_params(activity, 'ok_values', ok_values)
    cancel_value = override_app_params(activity, 'cancel_value', cancel_value)

    if request.method == 'POST':
        submit_value = request.POST[submit_name]
        if submit_value == cancel_value:
            return HttpResponseRedirect(redirect)
        
        if submit_value in ok_values:
            instance.condition = submit_value
            instance.save()
            completeWorkitem(workitem, request.user)
            return HttpResponseRedirect(redirect)
    return render_to_response(template, {'object':obj,
                                         'instance':instance,
                                         'submit_name':submit_name,
                                         'ok_values':ok_values,
                                         'cancel_value':cancel_value,
                                         'title':title,})


def override_app_params(activity, name, value):
    '''
    usage: param = _override_app_params(activity, 'param', param)
    '''
    try:
        if not activity.app_param:
            return value
        dicparams = eval(activity.app_param)
        if dicparams.has_key(name):
            return dicparams[name]
    except Exception, v:
        _logger.error('_override_app_params %s %s - %s', activity, name, v)
    return value
