#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import Process, Activity, Transition
from goflow.instances.models import Instance, WorkItem, Event
from django.contrib.auth.models import User, Group
from django.conf import settings
#from openflow.urls import WF_PUSH_APPS
from notification import notify_if_needed

from django.core.urlresolvers import resolve

import logger, logging
_logger = logging.getLogger('workflow.log')

def addProcess(title, description):
    process = Process.objects.create(title=title,
                                     description=description)
    process.begin = Activity.objects.create(title='initial', process=process)
    #process.end = Activity.objects.create(title='final', process=process)
    process.save()
    return process

def addInstance(user, title, object_inst):
    i = Instance(user=user, title=title, content_object=object_inst)
    i.save()
    return i

def check_start_instance_perm(process_name, user):
    if not isProcessEnabled(process_name):
        raise Exception('process %s disabled.' % process_name)
    if user.has_perm("workflow.can_instantiate"):
        l = user.groups.filter(name=process_name)
        if l.count()==0 or l[0].permissions.filter(codename='can_instantiate').count() == 0:
            raise Exception('permission needed to instantiate process %s.' % process_name)
    else:
        raise Exception('permission needed.')
    return

def startInstance(processName, user, item, title=None):
    '''
    return workitem
    '''
    p = Process.objects.get(title=processName, enabled=True)
    if not title or title=='instance':
        title = '%s %s' % (processName, str(item))
    instance = addInstance(user, title, item)
    instance.process = p
    # instance running
    instance.setStatus('r')
    instance.save()

    wi = WorkItem.objects.create(instance=instance, user=user, activity=p.begin)
    Event.objects.create(name='creation by %s' % user.username, workitem=wi)
    
    _logger.info('startInstance process %s user %s item %s', processName, user.username, item)

    if p.begin.autoStart:
        _logger.info('run auto activity %s workitem %s', p.begin.title, str(wi))
        user = User.objects.get(username=settings.WF_USER_AUTO)
        activateWorkitem(wi, actor=user)
        if execAutoApplication(wi):
            completeWorkitem(wi, actor=user)
        return wi
    
    if p.begin.pushApplication:
        userdest = execPushApplication(wi)
        _logger.info('application pushed to user %s', userdest.username)
        wi.user = userdest
        wi.save()
        Event.objects.create(name='assigned to %s' % userdest.username, workitem=wi)
        notify_if_needed(user=userdest)
    else:
        # set pull roles; useful (in activity too)?
        wi.pullRoles = wi.activity.roles.all()
        wi.save() 
        notify_if_needed(roles=wi.pullRoles)
        
    return wi

def forwardWorkItem(workitem, path=None, timeoutForwarding=False, sublow_workitem=None):
    _logger.info('forwardWorkItem %s', str(workitem))
    if not timeoutForwarding:
        if workitem.status != 'c':
            return
    if workitem.hasWorkItemsTo() and not sublow_workitem:
        _logger.debug('forwardWorkItem canceled for %s: workitem.hasWorkItemTo()', str(workitem))
        return
    
    if timeoutForwarding:
        _logger.info('timeout forwarding')
        Event.objects.create(name='timeout', workitem=workitem)
    
    for dest in getDestinations(workitem, timeoutForwarding):
        _forward_workitem_to_activity(workitem, dest)

def _forward_workitem_to_activity(workitem, dest):
    instance = workitem.instance
    wi = WorkItem.objects.create(instance=instance, user=None, activity=dest)
    _logger.info('forwarded to %s', dest.title)
    Event.objects.create(name='creation by %s' % workitem.user.username, workitem=wi)
    Event.objects.create(name='forwarded to %s' % dest.title, workitem=workitem)
    wi.workitemFrom = workitem
    if dest.autoStart:
        _logger.info('run auto activity %s workitem %s', dest.title, str(wi))
        try:
            user = User.objects.get(username=settings.WF_USER_AUTO)
        except Exception:
            raise Exception('a user named %s (settings.WF_USER_AUTO) must be defined for auto activities' % settings.WF_USER_AUTO)
        activateWorkitem(wi, actor=user)
        if execAutoApplication(wi):
            completeWorkitem(wi, actor=user)
        return wi
    
    if dest.pushApplication:
        userdest = execPushApplication(wi)
        _logger.info('application pushed to user %s', userdest.username)
        wi.user = userdest
        wi.save()
        Event.objects.create(name='assigned to %s' % userdest.username, workitem=wi)
        notify_if_needed(user=userdest)
    else:
        wi.pullRoles = wi.activity.roles.all()
        wi.save() 
        notify_if_needed(roles=wi.pullRoles)
    return wi

def getDestinations(workitem, path=None, timeoutForwarding=False):
    activity = workitem.activity
    transitions = Transition.objects.filter(input=activity)
    if timeoutForwarding:
        transitions = transitions.filter(condition__contains='workitem.time_out')
    destinations = []
    for t in transitions:
        if eval_transition_condition(t, workitem): destinations.append(t.output)
    return destinations

def pullWorkList(user):
    return {}

def _my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def execAutoApplication(workitem):
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
        func(request=None, workitem=workitem , **kwargs)
        return True
    except Exception, v:
        _logger.error('execution wi %s:%s', workitem, v)
    return False


def default_auto_app(workitem):
    ob = workitem.instance.wfobject()
    ob.history += '\n>>> execute auto activity: [%s]' % workitem.activity.title
    ob.save()
    return True


def execPushApplication(workitem):
    if not workitem.activity.process.enabled:
        raise Exception('process %s disabled.' % workitem.activity.process.title)
    appname = workitem.activity.pushApplication.url
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
            _logger.error('execPushApplication %s', v)
            result = None
            workitem.fallOut()
        return result
    
    try:
        prefix = settings.WF_PUSH_APPS_PREFIX
        # dyn import
        exec 'import %s' % prefix
        
        appname = '%s.%s' % (prefix, appname)
        result = eval('%s(workitem)' % appname)
    except Exception, v:
        _logger.error('execPushApplication %s', v)
        result = None
        workitem.fallOut()
    return result

def getWorkItems(user=None, username=None, activity=None, status=None, notstatus=('b','s','f','c'), noauto=True):
    u""" get workitems (in order to display a task list for example).
    
    user or username: filter on user (default=all)
    activity: filter on activity (default=all)
    status: filter on status (default=all)
    notstatus: list of status to exclude (default is a list of these: blocked, suspended, fallout, complete)
    noauto: if True (default) auto activities are excluded.
    """
    groups = Group.objects.all()
    if user:
        q = WorkItem.objects.filter(user=user, activity__process__enabled=True)
        groups = user.groups.all()
    else:
        if username:
            q = WorkItem.objects.filter(user__username=username, activity__process__enabled=True)
            groups = User.objects.get(username=username).groups.all()
        else:
            q = None
    if q:
        if status: q = q.filter(status=status)
        
        if notstatus:
            q = q.exclude(status=notstatus)
        else:
            for s in notstatus: q = q.exclude(status=s)
        
        if noauto: q = q.exclude(activity__autoStart=True)
    
        if activity: q = q.filter(activity=activity)
            
        q = list(q)
    else:
        q = []
        
    # search pullable workitems
    for role in groups:
        pullables = WorkItem.objects.filter(pullRoles=role, activity__process__enabled=True)
        if status: pullables = pullables.filter(status=status)
        if notstatus:
            pullables = pullables.exclude(status=notstatus)
        else:
            for s in notstatus: pullables = pullables.exclude(status=s)
        
        if noauto: pullables = pullables.exclude(activity__autoStart=True)        
        if activity: pullables = pullables.filter(activity=activity)
            
        if user:
            pp = pullables.filter(user__isnull=True) # tricky
            pullables = pullables.exclude(user=user)
            q.extend(list(pp))
        if username:
            pullables = pullables.exclude(user__username=username)
            
        _logger.debug('pullables workitems role %s: %s', role, str(pullables))
        q.extend(list(pullables))       
    return q


def activateWorkitem(workitem, actor):
    _checkWorkItem(workitem, actor, ('i', 'a'))
    if workitem.status=='a':
        _logger.warning('activateWorkitem actor %s workitem %s already active', actor.username, str(workitem))
        return
    workitem.status = 'a'
    workitem.user = actor
    workitem.save()
    _logger.info('activateWorkitem actor %s workitem %s', actor.username, str(workitem))
    Event.objects.create(name='activated by %s' % actor.username, workitem=workitem)

def completeWorkitem(workitem, actor):
    _checkWorkItem(workitem, actor, 'a')
    workitem.status = 'c'
    workitem.user = actor
    workitem.save()
    _logger.info('completeWorkitem actor %s workitem %s', actor.username, str(workitem))
    Event.objects.create(name='completed by %s' % actor.username, workitem=workitem)
    
    if workitem.activity.autoFinish:
        _logger.debug('activity autofinish: forward')
        forwardWorkItem(workitem)
    # if end activity, instance is complete
    if workitem.instance.process.end == workitem.activity:
        _logger.info('activity end process %s' % workitem.instance.process.title)
        # first test subflow
        lwi = WorkItem.objects.filter(activity__subflow=workitem.instance.process, status='b', instance=workitem.instance)
        if lwi.count() > 0:
            _logger.info('parent process for subflow %s' % workitem.instance.process.title)
            workitem0 = lwi[0]
            workitem0.instance.process = workitem0.activity.process
            workitem0.instance.save()
            _logger.info('process change for instance %s' % workitem0.instance.title)
            workitem0.status='c'
            workitem0.save()
            forwardWorkItem(workitem0, sublow_workitem=workitem)
        else:
            workitem.instance.setStatus('c')

def startSubflow(workitem, actor):
    begin_sub = workitem.activity.subflow.begin
    inst = workitem.instance
    inst.process = workitem.activity.subflow
    inst.save()
    workitem.status = 'b'
    workitem.blocked = True
    workitem.save()
    
    sub_workitem = _forward_workitem_to_activity(workitem, begin_sub)
    return sub_workitem

def getInstance(id):
    inst = Instance.objects.get(id=id)
    return inst

def getWorkItem(id, user=None, even_process_disabled=False, status=('i','a')):
    wi = WorkItem.objects.get(id=id, activity__process__enabled=True)
    if even_process_disabled:
        wi = WorkItem.objects.get(id=id)
    _checkWorkItem(wi, user, status)
    return wi

def isProcessEnabled(title):
    process = Process.objects.get(title=title)
    return process.enabled
    return False

def _checkWorkItem(workitem, user, status=('i','a')):
    if type(status)==type(''): status = (status,)
    if not workitem.activity.process.enabled:
        err = 'process %s disabled.' % workitem.activity.process.title
        _logger.error('workflow.api._checkWorkItem: %s' % err)
        raise Exception(err)
    if not workitem.check_user(user):
        err = 'user %s cannot take workitem %d.' % (user.username,workitem.id)
        _logger.error('workflow.api._checkWorkItem: %s' % err)
        workitem.fallOut()
        raise Exception(err)
    if not workitem.status in status:
        err = 'workitem %d has not a correct status (%s/%s).' % (workitem.id, workitem.status, str(status))
        _logger.error('workflow.api._checkWorkItem: %s' % err)
        raise Exception(err)
    return

def eval_transition_condition(transition, workitem):
    if not transition.condition: return True
    
    instance = workitem.instance
    wfobject = instance.wfobject()
    _logger.debug('eval_transition_condition %s - %s', transition.condition, instance.condition)
    try:
        result = eval(transition.condition)
        
        # boolean expr
        if type(result) == type(True):
            return result
        if type(result) == type(''):
            return (instance.condition==result)
    except Exception, v:
        _logger.debug('eval_transition_condition [%s]: %s', transition.condition, v)
        return (instance.condition==transition.condition)
        #_logger.error('eval_transition_condition [%s]: %s', transition.condition, v)
    return False
