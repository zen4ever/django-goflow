#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''
Location: goflow.workflow.api

Purpose: Provides api for accessing commonly used 
         workflow functionality in goflow

'''
from models import Process, Activity, Transition
from goflow.instances.models import ProcessInstance, WorkItem, Event
from django.contrib.auth.models import User, Group
from django.conf import settings
from notification import notify_if_needed

from django.core.urlresolvers import resolve

# import logger #(was not being used)
import logging
_log = logging.getLogger('workflow.log')

def add_process(title, description):
    '''
    Creates, saves, and returns a Process instance
    and adds an intital activity to it.
    
    @type title: string
    @param title: the title of the new Process instance.
    @type description: string
    @param description: a short description of the new Process instance.
    @rtype: Process
    @return: a newly saved Process instance.
    '''
    process = Process.objects.create(title=title, description=description)
    process.begin = Activity.objects.create(title='initial', process=process)
    # TODO: why not include also a final activity
    #process.end = Activity.objects.create(title='final', process=process)
    process.save()
    return process

def add_instance(user, title, obj_instance):
    '''
    Returns a newly saved ProcessInstance instance.
    
    @type user: User
    @param user: an instance of django.contrib.auth.models.User, 
                 typically retrieved through a request object.
    @type title: string
    @param title: the title of the new ProcessInstance instance.
    @type obj_instance: ContentType
    @param obj_instance: an instance of ContentType, which is typically
                        associated with a django Model. In this case???
    @rtype: ProcessInstance
    @return: a newly saved ProcessInstance instance.
    
    '''
    instance = ProcessInstance(user=user, title=title, content_object=obj_instance)
    instance.save()
    return instance

def check_start_instance_perm(process_name, user):
    '''
    Checks whether a process is enabled and whether the user has permission
    to instantiate it; raises exceptions if not the case, returns None otherwise.
    
    @type process_name: string
    @param process_name: a name of a process. e.g. 'leave'
    @type user: User
    @param user: an instance of django.contrib.auth.models.User, 
                 typically retrieved through a request object.
    @rtype:
    @return: passes silently if checks are met, 
             raises exceptions otherwise.
    '''
    if not is_process_enabled(process_name):
        raise Exception('process %s disabled.' % process_name)
    
    if user.has_perm("workflow.can_instantiate"):
        lst = user.groups.filter(name=process_name)
        if lst.count()==0 or \
           (lst[0].permissions.filter(codename='can_instantiate').count() == 0):
            raise Exception('permission needed to instantiate process %s.' % process_name)
    else:
        raise Exception('permission needed.')
    return

def start_instance(process_name, user, item, title=None):
    '''
    Returns a workitem given the name of a preexisting enabled Process 
    instance, while passing in the id of the user, the contenttype 
    object and the title.
    
    @type process_name: string
    @param process_name: a name of a process. e.g. 'leave'
    @type user: User
    @param user: an instance of django.contrib.auth.models.User, 
                 typically retrieved through a request object.
    @type item: ContentType
    @param item: a content_type object e.g. an instance of LeaveRequest
    @type: title: string
    @param title: title of new ProcessInstance instance (optional)
    @rtype: WorkItem
    @return: a newly configured workitem sent to auto_user, 
             a target_user, or ?? (roles).
    '''
    process = Process.objects.get(title=process_name, enabled=True)
    if not title or (title=='instance'):
        title = '%s %s' % (process_name, __unicode__(item))
    instance = add_instance(user, title, item)
    instance.process = process
    # instance running
    instance.set_status('running')
    instance.save()
    
    workitem = WorkItem.objects.create(instance=instance, user=user, activity=process.begin)
    Event.objects.create(name='creation by %s' % user.username, workitem=workitem)
    
    _log.info('start_instance process %s user %s item %s', process_name, 
        user.username, item)

    if process.begin.autostart:
        _log.info('run auto activity %s workitem %s', process.begin.title, str(workitem))
        auto_user = User.objects.get(username=settings.WF_USER_AUTO)
        activate_workitem(workitem, actor=auto_user)
        if exec_auto_application(workitem):
            complete_workitem(workitem, actor=auto_user)
        return workitem
    
    if process.begin.push_application:
        target_user = exec_push_application(workitem)
        _log.info('application pushed to user %s', target_user.username)
        workitem.user = target_user
        workitem.save()
        Event.objects.create(name='assigned to %s' % target_user.username, workitem=workitem)
        notify_if_needed(user=target_user)
    else:
        # set pull roles; useful (in activity too)?
        workitem.pull_roles = workitem.activity.roles.all()
        workitem.save()
        notify_if_needed(roles=workitem.pull_roles)
    
    return workitem

def forward_workitem(workitem, timeout_forwarding=False, subflow_workitem=None):
    # forward_workitem(workitem, path=None, timeout_forwarding=False, subflow_workitem=None):
    '''
    Convenience procedure to forwards workitems to valid destination activities.
    
    @type workitem: WorkItem
    @param workitem: an instance of WorkItem
    @type path: string??
    @param path: XXX TODO: This is not used, so don't know why it's here.
    @type timeoutForwarding: bool
    @param timeoutForwarding:
    @type: subflow_workitem: WorkItem
    @param subflow_workitem: a workitem associated with a subflow ???
    
    '''
    _log.info('forward_workitem %s', str(workitem))
    if not timeout_forwarding:
        if workitem.status != 'complete':
            return
    if workitem.has_workitems_to() and not subflow_workitem:
        _log.debug('forward_workitem canceled for %s: ' 
                   'workitem.has_workitem_to()', str(workitem))
        return
    
    if timeout_forwarding:
        _log.info('timeout forwarding')
        Event.objects.create(name='timeout', workitem=workitem)
    
    for destination in get_destinations(workitem, timeout_forwarding):
        _forward_workitem_to_activity(workitem, destination)

def _forward_workitem_to_activity(workitem, target_activity):
    '''
    Passes the process instance embedded in the given workitem 
    to a new workitem that is associated with the destination activity.
    
    @type workitem: WorkItem
    @param workitem: an instance of WorkItem
    @type target_activity: Activity
    @param target_activity: the activity instance to which the workitem 
                            should be forwarded
    @rtype: WorkItem
    @return: a workitem that has been passed on to the next 
             activity (and next user)
    '''
    instance = workitem.instance
    wi = WorkItem.objects.create(instance=instance, user=None, activity=target_activity)
    _log.info('forwarded to %s', target_activity.title)
    Event.objects.create(name='creation by %s' % workitem.user.username, workitem=wi)
    Event.objects.create(name='forwarded to %s' % target_activity.title, workitem=workitem)
    wi.workitem_from = workitem
    if target_activity.autostart:
        _log.info('run auto activity %s workitem %s', target_activity.title, str(wi))
        try:
            auto_user = User.objects.get(username=settings.WF_USER_AUTO)
        except Exception:
            error = 'a user named %s (settings.WF_USER_AUTO) must be defined for auto activities'
            raise Exception(error % settings.WF_USER_AUTO)
        activate_workitem(wi, actor=auto_user)
        if exec_auto_application(wi):
            complete_workitem(wi, actor=auto_user)
        return wi
    
    if target_activity.push_application:
        target_user = exec_push_application(wi)
        _log.info('application pushed to user %s', target_user.username)
        wi.user = target_user
        wi.save()
        Event.objects.create(name='assigned to %s' % target_user.username, workitem=wi)
        notify_if_needed(user=target_user)
    else:
        wi.pull_roles = wi.activity.roles.all()
        wi.save()
        notify_if_needed(roles=wi.pull_roles)
    return wi

def get_destinations(workitem, timeout_forwarding=False):
    #get_destinations(workitem, path=None, timeout_forwarding=False):
    '''
    Return list of destination activities that meet the conditions of each transition
    
    @type workitem: WorkItem
    @param workitem: an instance of Workitem
    @type path: string??
    @param path: XXX TODO: This is not used, so don't know why it's here.
    @type timeout_forwarding: bool
    @param timeout_forwarding: a workitem with a time-delay??
    @rtype: [Activity]
    @return: list of destination activities.
    '''
    activity = workitem.activity
    transitions = Transition.objects.filter(input=activity)
    if timeout_forwarding:
        transitions = transitions.filter(condition__contains='workitem.time_out')
    destinations = []
    for t in transitions:
        if eval_transition_condition(t, workitem):
            destinations.append(t.output)
    return destinations

def pull_worklist(user):
    return {}

def _my_import(name):
    '''
    import utility function
    @rtype: Module
    '''
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def exec_auto_application(workitem):
    '''
    creates a test auto application for activities that don't yet have applications
    @type workitem: WorkItem
    @rtype: bool
    '''
    try:
        if not workitem.activity.process.enabled:
            raise Exception('process %s disabled.' % workitem.activity.process.title)
        # no application: default auto app
        if not workitem.activity.application:
            return default_auto_app(workitem)
        
        func, args, kwargs = resolve(workitem.activity.application.get_app_url())
        params = workitem.activity.app_param
        # params values defined in activity override those defined in urls.py
        if params:
            params = eval('{'+params.lstrip('{').rstrip('}')+'}')
            kwargs.update(params)
        func(workitem=workitem , **kwargs)
        return True
    except Exception, v:
        _log.error('execution wi %s:%s', workitem, v)
    return False


def default_auto_app(workitem):
    '''
    retrieves wfobject, logs info to it saves
    
    @rtype: bool
    @return: always returns True
    '''
    obj = workitem.instance.wfobject()
    obj.history += '\n>>> execute auto activity: [%s]' % workitem.activity.title
    obj.save()
    return True


def exec_push_application(workitem):
    '''
    Execute push application in workitem
    '''
    if not workitem.activity.process.enabled:
        raise Exception('process %s disabled.' % workitem.activity.process.title)
    appname = workitem.activity.push_application.url
    params = workitem.activity.pushapp_param
    # try std pushapps:
    import pushapps
    if appname in dir(pushapps):
        try:
            kwargs = ''
            if params:
                kwargs = ',**%s' % params
            result = eval('pushapps.%s(workitem%s)' % (appname, kwargs))
        except Exception, v:
            _log.error('exec_push_application %s', v)
            result = None
            workitem.fall_out()
        return result
    
    try:
        prefix = settings.WF_PUSH_APPS_PREFIX
        # dyn import
        exec 'import %s' % prefix
        
        appname = '%s.%s' % (prefix, appname)
        result = eval('%s(workitem)' % appname)
    except Exception, v:
        _log.error('exec_push_application %s', v)
        result = None
        workitem.fall_out()
    return result

def get_workitems(user=None, username=None, queryset=WorkItem.objects, activity=None, status=None,
                  notstatus=('blocked','suspended','fallout','complete'), noauto=True):
    """
    get workitems (in order to display a task list for example).
    
    user or username: filter on user (default=all)
    queryset: pre-filtering (default=WorkItem.objects)
    activity: filter on activity (default=all)
    status: filter on status (default=all)
    notstatus: list of status to exclude
               (default is a list of these: blocked, suspended, fallout, complete)
    noauto: if True (default) auto activities are excluded.
    """
    if status:
        notstatus = []
    
    groups = Group.objects.all()
    if user:
        query = queryset.filter(user=user, activity__process__enabled=True)
        groups = user.groups.all()
    else:
        if username:
            query = queryset.filter(
                    user__username=username, 
                    activity__process__enabled=True
            )
            groups = User.objects.get(username=username).groups.all()
        else:
            query = None
    if query:
        if status:
            query = query.filter(status=status)
        
        if notstatus:
            for status in notstatus: 
                query = query.exclude(status=status)
        
        if noauto:
            query = query.exclude(activity__autostart=True)
        
        if activity:
            #TODO: this is not used...??
            sq = query.filter(activity=activity)
        
        query = list(query)
    else:
        query = []
    
    # search pullable workitems
    for role in groups:
        pullables = queryset.filter(pull_roles=role, activity__process__enabled=True)
        if status:
            pullables = pullables.filter(status=status)
        
        if notstatus:
            for status in notstatus:
                pullables = pullables.exclude(status=status)
        
        if noauto:
            pullables = pullables.exclude(activity__autostart=True)
        
        if activity:
            pullables = pullables.filter(activity=activity)
        
        if user:
            pp = pullables.filter(user__isnull=True) # tricky
            pullables = pullables.exclude(user=user)
            query.extend(list(pp))
        
        if username:
            pullables = pullables.exclude(user__username=username)
        
        _log.debug('pullables workitems role %s: %s', role, str(pullables))
        query.extend(list(pullables))
    
    return query

# TODO: activate_workitem and complete_workitem can possibly be refactored
# and combined into one change_workitem_status(workitem, actor) function
def activate_workitem(workitem, actor):
    '''
    changes workitem status to 'active' and logs event, activator
    
    '''
    _check_workitem(workitem, actor, ('inactive', 'active'))
    if workitem.status == 'active':
        _log.warning('activate_workitem actor %s workitem %s already active', 
            actor.username, str(workitem))
        return
    workitem.status = 'active'
    workitem.user = actor
    workitem.save()
    _log.info('activate_workitem actor %s workitem %s', 
        actor.username, str(workitem))
    Event.objects.create(name='activated by %s' % actor.username, workitem=workitem)

def complete_workitem(workitem, actor):
    '''
    changes status of workitem to 'complete' and logs event
    '''
    _check_workitem(workitem, actor, 'active')
    workitem.status = 'complete'
    workitem.user = actor
    workitem.save()
    _log.info('complete_workitem actor %s workitem %s', actor.username, str(workitem))
    Event.objects.create(name='completed by %s' % actor.username, workitem=workitem)
    
    if workitem.activity.autofinish:
        _log.debug('activity autofinish: forward')
        forward_workitem(workitem)
    
    # if end activity, instance is complete
    if workitem.instance.process.end == workitem.activity:
        _log.info('activity end process %s' % workitem.instance.process.title)
        # first test subflow
        lwi = WorkItem.objects.filter(activity__subflow=workitem.instance.process,
                                      status='blocked',
                                      instance=workitem.instance)
        if lwi.count() > 0:
            _log.info('parent process for subflow %s' % workitem.instance.process.title)
            workitem0 = lwi[0]
            workitem0.instance.process = workitem0.activity.process
            workitem0.instance.save()
            _log.info('process change for instance %s' % workitem0.instance.title)
            workitem0.status = 'complete'
            workitem0.save()
            forward_workitem(workitem0, subflow_workitem=workitem)
        else:
            workitem.instance.set_status('complete')

def start_subflow(workitem, actor):
    '''
    starts subflow and blocks passed in workitem
    '''
    subflow_begin_activity = workitem.activity.subflow.begin
    instance = workitem.instance
    instance.process = workitem.activity.subflow
    instance.save()
    workitem.status = 'blocked'
    workitem.blocked = True
    workitem.save()
    
    sub_workitem = _forward_workitem_to_activity(workitem, subflow_begin_activity)
    return sub_workitem

def get_instance(id):
    '''
    get ProcessInstance instance by id
    '''
    instance = ProcessInstance.objects.get(id=id)
    return instance

def get_workitem(id, user=None, even_process_disabled=False, status=('inactive','active')):
    '''
    get WorkItem instance by 
    '''
    workitem = WorkItem.objects.get(id=id, activity__process__enabled=True)
    if even_process_disabled:
        workitem = WorkItem.objects.get(id=id)
    _check_workitem(workitem, user, status)
    return workitem

def is_process_enabled(title):
    '''
    determines if a process is enabled or otherwise
    @rtype: bool
    '''
    process = Process.objects.get(title=title)
    return process.enabled 
    #return False 
    # TODO: this was hardwired to false ???

def _check_workitem(workitem, user, status=('inactive','active')):
    '''
    helper function to determine whether process is:
        - enabled, etc..
    
    '''
    if type(status)==type(''):
        status = (status,)
        
    if not workitem.activity.process.enabled:
        error = 'process %s disabled.' % workitem.activity.process.title
        _log.error('workflow.api._checkWorkItem: %s' % error)
        raise Exception(error)
        
    if not workitem.check_user(user):
        error = 'user %s cannot take workitem %d.' % (user.username, workitem.id)
        _log.error('workflow.api._check_workitem: %s' % error)
        workitem.fall_out()
        raise Exception(error)
        
    if not workitem.status in status:
        error = 'workitem %d has not a correct status (%s/%s).' % (
            workitem.id, workitem.status, str(status))
        _log.error('workflow.api._check_workitem: %s' % error)
        raise Exception(error)

    return

def eval_transition_condition(transition, workitem):
    '''
    evaluate the condition of a transition
    '''
    if not transition.condition:
        return True
    instance = workitem.instance
    wfobject = instance.wfobject()
    _log.debug('eval_transition_condition %s - %s', 
        transition.condition, instance.condition)
    try:
        result = eval(transition.condition)
        
        # boolean expr
        if type(result) == type(True):
            return result
        if type(result) == type(''):
            return (instance.condition==result)
    except Exception, v:
        _log.debug('eval_transition_condition [%s]: %s', transition.condition, v)
        return (instance.condition==transition.condition)
        #_log.error('eval_transition_condition [%s]: %s', transition.condition, v)
    return False
