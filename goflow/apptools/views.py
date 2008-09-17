#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.contenttypes.models import ContentType
from forms import ContentTypeForm

from goflow.workflow.models import Process, Application, Transition
from goflow.runtime.models import ProcessInstance, WorkItem

from django.db import models
from django.contrib.auth.models import User
from django.forms.models import modelform_factory

from django.contrib.auth.decorators import permission_required

from django.contrib.auth.decorators import login_required
from models import DefaultAppModel, Icon, Image, ImageButton
from forms import DefaultAppForm

from django.conf import settings

from goflow.workflow.logger import Log; log = Log('goflow.apptools.views')

from goflow.workflow.notification import send_mail

@login_required
def start_application(request, app_label=None, model_name=None, process_name=None, instance_label=None,
                       template=None, template_def='goflow/start_application.html',
                       form_class=None, redirect='home', submit_name='action',
                       ok_value='OK', cancel_value='Cancel', extra_context={}):
    '''
    generic handler for application that enters a workflow.
    
    parameters:
    
    app_label, model_name
        model linked to workflow instance (deprecated)
    process_name
        default: same name as app_label
    instance_label
        default: process_name + str(object)
    template 
        default: 'start_%s.html' % app_label
    template_def
        used if template not found - default: 'goflow/start_application.html'
    form_class
        default: django.forms.models.modelform_factory(model)
    '''
    if not process_name:
        process_name = app_label
    try:
        Process.objects.check_can_start(process_name, request.user)
    except Exception, v:
        return HttpResponse(str(v))
    
    #if not instance_label: instance_label = '%s-%s' % (app_label, model_name)
    if not template: template = 'start_%s.html' % app_label
    if not form_class:
        model = models.get_model(app_label, model_name)
        form_class = modelform_factory(model)
        is_form_used = False
    else:
        is_form_used = True
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
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
                    log.error("the save method of the form must accept parameters user and data")
                else:
                    log.error("forme save error: %s", str(v))
            
            if ob:
                priority = int(form.cleaned_data['priority'])
                ProcessInstance.objects.start(process_name, request.user, ob, instance_label, priority=priority)
            
            return HttpResponseRedirect(redirect)
    else:
        form = form_class()
        # precheck
        form.pre_check(user=request.user)
    context = {'form': form, 'process_name':process_name,
               'submit_name':submit_name, 'ok_value':ok_value, 'cancel_value':cancel_value}
    context.update(extra_context)
    return render_to_response((template, template_def), context,
                              context_instance=RequestContext(request))


@login_required
def default_app(request, id, template='goflow/default_app.html', redirect='../../', submit_name='action'):
    '''
    default application, used for prototyping workflows.
    '''
    submit_values = ('OK', 'Cancel')
    id = int(id)
    if request.method == 'POST':
        data = request.POST.copy()
        workitem = WorkItem.objects.get_safe(id, user=request.user)
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
            
            workitem.complete(request.user)
            return HttpResponseRedirect(redirect)
    else:
        workitem = WorkItem.objects.get_safe(id, user=request.user)
        inst = workitem.instance
        ob = inst.wfobject()
        form = DefaultAppForm(instance=ob)
        # add header with activity description, submit buttons dynamically
        if workitem.activity.split_mode == 'x':
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
                                         'submit_values':submit_values,},
                              context_instance=RequestContext(request))


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
def edit_model(request, id, form_class, cmp_attr=None,template=None, template_def='goflow/edit_model.html', title="",
               redirect='home', submit_name='action', ok_values=('OK',), save_value=None, cancel_value='Cancel',
               extra_context={}):
    '''
    generic handler for editing a model.
    
    parameters:

    id
        workitem id (required)
    form_class
        model form based on goflow.apptools.forms.BaseForm (required)
    cmp_attr
        edit obj.cmp_attr attribute instead of obj - default=None
    template 
        default: 'goflow/edit_%s.html' % model_lowercase
    template_def
        used if template not found - default: 'goflow/edit_model.html'
    title
        default=""
    redirect
        default='home'
    submit_name
        name for submit buttons - default='action'
    ok_values
        submit buttons values - default=('OK',)
    save_value
        save button value - default='Save'
    cancel_value
        cancel button value - default='Cancel'
    extra_context
        default={}
    '''
    if not template: template = 'goflow/edit_%s.html' % form_class._meta.model._meta.object_name.lower()
    model_class = form_class._meta.model
    workitem = WorkItem.objects.get_safe(int(id), user=request.user)
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
                #ob = form.save()
                try:
                    ob = form.save(workitem=workitem, submit_value=submit_value)
                except Exception, v:
                    raise Exception(str(v))
                return HttpResponseRedirect(redirect)
            
            if submit_value in ok_values:
                # save and complete activity
                #ob = form.save()
                try:
                    ob = form.save(workitem=workitem, submit_value=submit_value)
                except Exception, v:
                    raise Exception(str(v))
                instance.condition = submit_value
                instance.save()
                workitem.complete(request.user)
                return HttpResponseRedirect(redirect)
    else:
        form = form_class(instance=obj)
        # precheck
        form.pre_check(obj_context, user=request.user)
    
    context = {  'form': form, 'object':obj, 'object_context':obj_context,
                 'instance':instance, 'workitem':workitem,
                 'submit_name':submit_name, 'ok_values':ok_values,
                 'save_value':save_value, 'cancel_value':cancel_value,
                 'title':title}
    context.update(extra_context)
    return render_to_response((template, template_def), context,
                              context_instance=RequestContext(request))


@login_required
def view_application(request, id, template='goflow/view_application.html', redirect='home', title="",
               submit_name='action', ok_values=('OK',), cancel_value='Cancel',
               extra_context={}):
    '''
    generic handler for a view application.
    
    useful for a simple view or a complex object edition.

    parameters:
    
    id
        workitem id (required)
    template 
        default: 'goflow/view_application.html'
    redirect
        default='home'
    title
        default=""
    submit_name
        name for submit buttons - default='action'
    ok_values
        submit buttons values - default=('OK',)
    cancel_value
        cancel button value - default='Cancel'
    extra_context
        default={}
    '''
    workitem = WorkItem.objects.get_safe(int(id), user=request.user)
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
            workitem.complete(request.user)
            return HttpResponseRedirect(redirect)
        
    context = {  'object':obj,'instance':instance, 'workitem':workitem,
                 'submit_name':submit_name,
                 'ok_values':ok_values,'cancel_value':cancel_value,
                 'title':title}
    context.update(extra_context)
    return render_to_response(template, context,
                              context_instance=RequestContext(request))


@login_required
def choice_application(request, id, template='goflow/view_application_image.html', redirect='home', title="Choice",
               submit_name='image', cancel_action='cancel', extra_context={}):
    '''
    a view to make a choice within image buttons.
    
    - actions are generated from instances conditions of outer transitions
    - the activity split_mode must be xor
    - actions are rendered with images
    - actions are mapped to images with ImageButton instances

    parameters:
    
    id
        workitem id (required)
    template 
        default: 'goflow/view_application_image.html'
    redirect
        default='home'
    title
        default='Choice'
    submit_name
        name for submit buttons - default='image'
    cancel_value
        cancel button value - default='Cancel'
    extra_context
        default={}
    '''
    workitem = WorkItem.objects.get_safe(int(id), user=request.user)
    activity = workitem.activity
    if activity.split_mode != 'xor':
        raise Exception('choice_application: split_mode xor required')
    list_trans = Transition.objects.filter(input=activity)
    ok_values = []
    for t in list_trans:
        if ImageButton.objects.filter(action=t.condition).count() == 0:
            raise Exception('no ImageButton for action [%s]' % t.condition)
        ok_values.append(t.condition)
        
    return view_application(request, id, template, redirect, title,
               submit_name, ok_values, cancel_action, extra_context)

def sendmail(workitem, subject='goflow.apptools sendmail message', template='goflow/app_sendmail.txt'):
    '''send a mail notification to the workitem user.
    
    parameters:
    
    subject
        default='goflow.apptools sendmail message'
    template
        default='goflow/app_sendmail.txt'
    '''
    send_mail(workitems=(workitem,), user=workitem.user, subject=subject, template=template)

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
        log.error('_override_app_params %s %s - %s', activity, name, v)
    return value


@login_required
def app_env(request, action, id, template=None):
    """
    creates/removes unit test environment for applications.
    
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
    
    rep += '<hr><p><b><a href=../../../>return</a></b>'
    return HttpResponse(rep)

@login_required
def test_start(request, id, template='goflow/test_start.html'):
    """
    starts test instances.
    
    for a given application, with its unit test environment, the user
    choose a content-type then generates unit test process instances
    by cloning existing content-type objects (**Work In Progress**).
    """
    app = Application.objects.get(id=int(id))
    context = {}
    if request.method == 'POST':
        submit_value = request.POST['action']
        if submit_value == 'Create':
            ctype = ContentType.objects.get(id=int(request.POST['ctype']))
            model = ctype.model_class()
            for inst in model.objects.all():
                # just objects without link to a workflow instance
                if ProcessInstance.objects.filter(
                    content_type__pk=ctype.id,
                    object_id=inst.id
                ).count() > 0:
                    continue
                inst.id = None
                inst.save()
                #TODO: convert this to method
                ProcessInstance.objects.start(
                #start_instance(
                            process_name='test_%s' % app.url,
                            user=request.user, item=inst, 
                            title="%s test instance for app %s" % (
                                ctype.name, app.url
                            ))
            request.user.message_set.create(message='test instances created')
        return HttpResponseRedirect('../..')
    form = ContentTypeForm()
    context['form'] = form
    return render_to_response(template, context)


@login_required
def image_update(request):
    '''
    Import Image instances as Icon instances.
    
    GoFlow can use local images as well as http distant images.
    For a genericity reason, local images (Image) are obtained as
    Icon images by their url; this view is useful to wrap all local
    images in a row. 
    '''
    rep = '<h1>Update Icons from Images</h1>'
    for im in Image.objects.all():
        if Icon.objects.filter(url__endswith=str(im.url)).count() == 0:
            ic, created = Icon.objects.get_or_create(category='local-'+im.category, url=im.url())
            if created: rep += '<br> %s added ' % im.url()
    rep += '<hr><p><b><a href=../>return</a></b>'
    return HttpResponse(rep)
    
    