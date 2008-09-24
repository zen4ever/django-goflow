#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import Group, User
from goflow.workflow.models import Process, Activity, Transition, UserProfile
from goflow.workflow.notification import send_mail
from datetime import timedelta, datetime
from django.core.urlresolvers import resolve
from django.core.mail import mail_admins

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from goflow.workflow.logger import Log; log = Log('goflow.runtime.managers')
from django.conf import settings

from goflow.workflow.decorators import allow_tags

class ProcessInstanceManager(models.Manager):
    '''Custom model manager for ProcessInstance
    '''
   
    def start(self, process_name, user, item, title=None, priority=0):
        '''
        Returns a workitem given the name of a preexisting enabled Process 
        instance, while passing in the id of the user, the contenttype 
        object and the title.
        
        :type process_name: string
        :param process_name: a name of a process. e.g. 'leave'
        :type user: User
        :param user: an instance of django.contrib.auth.models.User, 
                     typically retrieved through a request object.
        :type item: ContentType
        :param item: a content_type object e.g. an instance of LeaveRequest
        :type: title: string
        :param title: title of new ProcessInstance instance (optional)
        :type: priority: integer
        :param priority: default priority (optional)
        :rtype: WorkItem
        :return: a newly configured workitem sent to auto_user, 
                 a target_user, or ?? (roles).
        
        usage::
            
            wi = Process.objects.start(process_name='leave', 
                                       user=admin, item=leaverequest1)

        '''
        
        process = Process.objects.get(title=process_name, enabled=True)
        if priority == 0: priority = process.priority
            
        if not title or (title=='instance'):
            title = '%s %s' % (process_name, str(item))
        instance = ProcessInstance.objects.create(process=process, user=user, title=title, content_object=item)
        # instance running
        instance.set_status('running')
        
        workitem = WorkItem.objects.create(instance=instance, user=user, 
                                           activity=process.begin, priority=priority)
        log.event('created by ' + user.username, workitem)
        log('process:', process_name, 'user:', user.username, 'item:', item)
    
        if process.begin.kind == 'dummy':
            log('routing activity', process.begin.title, 'workitem:', workitem)
            auto_user = User.objects.get(username=settings.WF_USER_AUTO)
            workitem.activate(actor=auto_user)
            workitem.complete(actor=auto_user)
            return workitem
        
        if process.begin.autostart:
            log('run auto activity', process.begin.title, 'workitem:', workitem)
            auto_user = User.objects.get(username=settings.WF_USER_AUTO)
            workitem.activate(actor=auto_user)
    
            if workitem.exec_auto_application():
                log('workitem.exec_auto_application:', workitem)
                workitem.complete(actor=auto_user)
            return workitem

        if process.begin.push_application:
            target_user = workitem.exec_push_application()
            log('application pushed to user', target_user.username)
            workitem.user = target_user
            workitem.save()
            log.event('assigned to '+target_user.username, workitem)
            #notify_if_needed(user=target_user)
        else:
            # set pull roles; useful (in activity too)?
            workitem.pull_roles = workitem.activity.roles.all()
            workitem.save()
            #notify_if_needed(roles=workitem.pull_roles)
        
        return workitem


class ProcessInstance(models.Model):
    """ This is a process instance.
    
    A process instance is created when someone decides to do something,
    and doing this thing means start using a process defined in GoFlow.
    That's why it is called "process instance". The process is a class
    (=the definition of the process), and each time you want to
    "do what is defined in this process", that means you want to create
    an INSTANCE of this process.
    
    So from this point of view, an instance represents your dynamic
    part of a process. While the process definition contains the map
    of the workflow, the instance stores your usage, your history,
    your state of this process.
    
    The ProcessInstance will collect and handle workitems (see definition)
    to be passed from activity to activity in the process.
    
    Each instance can have more than one workitem depending on the
    number of split actions encountered in the process flow.
    That means that an instance is actually the collection of all of
    the instance "pieces" (workitems) that we get from splits of the
    same original process instance.
    
    Each ProcessInstance keeps track of its history through a graph.
    Each node of the graph represents an activity the instance has
    gone through (normal graph nodes) or an activity the instance is
    now pending on (a graph leaf node). Tracking the ProcessInstance history
    can be very useful for the ProcessInstance monitoring.
    
    When a process instance starts, the instance has to carry an
    implementation object that contains the application data. The
    specifications for the implementation class is:
    
    (nothing: now managed by generic relation)
    
    From the instance, the implementation object is reached as following:
      obj = instance.content_object (or instance.wfobject()).
    In a template, a field date1 will be displayed like this:
      {{ instance.wfobject.date1 }} or {{ instance.content_object.date1 }}
    
    From the object, instances may be reached with the reverse generic relation:
    the following can be added to the model:
      wfinstances = generic.GenericRelation(ProcessInstance)
    
    """
    STATUS_CHOICES = (
                      ('initiated', 'initiated'),
                      ('running', 'running'),
                      ('active', 'active'),
                      ('complete', 'complete'),
                      ('terminated', 'terminated'),
                      ('suspended', 'suspended'),
                      )
    title = models.CharField(max_length=100)
    process = models.ForeignKey(Process, related_name='instances', null=True, blank=True)
    creationTime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='instances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='initiated')
    old_status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    condition = models.CharField(max_length=50, null=True, blank=True)
    
    # refactoring
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    # add new ProcessInstanceManager
    objects = ProcessInstanceManager()
    
    def wfobject(self):
        return self.content_object
    
    @allow_tags
    def workitems_list(self):
        '''provide html link to workitems for a process instance in admin change list.
        @rtype: string
        @return: html href link "../workitem/?instance__id__exact=[self.id]&ot=asc&o=0"
        '''
        nbwi = self.workitems.count()
        return '<a href=../workitem/?instance__id__exact=%d&ot=asc&o=0>%d item(s)</a>' % (self.pk, nbwi)
    
    def __str__(self):
        return str(self.pk)
    
    def __unicode__(self):
        return self.title
    
    def set_status(self, status):
        if not status in [x for x,y in ProcessInstance.STATUS_CHOICES]:
            raise Exception('instance status incorrect :%s' % status)
        self.old_status = self.status
        self.status = status
        self.save()


class WorkItemManager(models.Manager):
    '''Custom model manager for WorkItem
    '''
    def get_safe(self, id, user=None, enabled_only=False, status=('inactive','active')):
        '''
        Retrieves a single WorkItem instance given a set of parameters
        
        :type id: int
        :param id: the id of the WorkItem instance
        :type user: User
        :param user: an instance of django.contrib.auth.models.User, 
                     typically retrieved through a request object.
        :type enabled_only: bool
        :param enabled_only: implies that only enabled processes should be queried
        :type status: tuple or string
        :param status: ensure that workitem has one of the given set of statuses
        
        usage::
        
            workitem = WorkItem.objects.get_safe(id, user=request.user)
        
        '''
        if enabled_only:
            workitem = self.get(id=id, activity__process__enabled=True)
        else:
            workitem = self.get(id=id)
        workitem._check(user, status)
        return workitem

    def list_safe(self, user=None, username=None, queryset='qs_default', activity=None, status=None,
                      notstatus=('blocked','suspended','fallout','complete'), noauto=True):
        """
        Retrieve list of workitems (in order to display a task list for example).
        
        :type user: User
        :param user: filter on instance of django.contrib.auth.models.User (default=all) 
        :type username: string
        :param username: filter on username of django.contrib.auth.models.User (default=all) 
        :type queryset: QuerySet
        :param queryset: pre-filtering (default=WorkItem.objects)
        :type activity: Activity
        :param activity: filter on instance of goflow.workflow.models.Activity (default=all) 
        :type status: string
        :param status: filter on status (default=all) 
        :type notstatus: string or tuple
        :param notstatus: list of status to exclude (default: [blocked, suspended, fallout, complete])
        :type noauto: bool
        :param noauto: if True (default) auto activities are excluded.
        
        usage::
        
            workitems = WorkItem.objects.list_safe(user=me, notstatus='complete', noauto=True)
        
        """
        if queryset == 'qs_default': queryset = WorkItem.objects
        if status: notstatus = []
        
        groups = Group.objects.all()
        if user:
            query = queryset.filter(user=user, activity__process__enabled=True).order_by('-priority')
            groups = user.groups.all()
        else:
            if username:
                query = queryset.filter(
                        user__username=username, 
                        activity__process__enabled=True
                ).order_by('-priority')
                groups = User.objects.get(username=username).groups.all()
            else:
                query = None
        if query:
            if status:
                query = query.filter(status=status)
            
            if notstatus:
                for s in notstatus: 
                    query = query.exclude(status=s)
            
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
            pullables = queryset.filter(pull_roles=role, activity__process__enabled=True).order_by('-priority')
            if status:
                pullables = pullables.filter(status=status)
            
            if notstatus:
                for s in notstatus:
                    pullables = pullables.exclude(status=s)
            
            if noauto:
                pullables = pullables.exclude(activity__autostart=True)
            
            if activity:
                pullables = pullables.filter(activity=activity)
            
            if user:
                pullables = pullables.filter(user__isnull=True) # tricky
                pullables = pullables.exclude(user=user)
                query.extend(list(pullables))
            
            if username:
                pullables = pullables.exclude(user__username=username)
            
            log.debug('pullables workitems role %s: %s', role, str(pullables))
            query.extend(list(pullables))
        
        # search workitems pullable by anybody
        pullables = queryset.filter(pull_roles__isnull=True,
                                    activity__process__enabled=True,
                                    user__isnull=True).order_by('-priority')
        if status:
            pullables = pullables.filter(status=status)
        if notstatus:
            for s in notstatus:
                pullables = pullables.exclude(status=s)
        if noauto:
            pullables = pullables.exclude(activity__autostart=True)
        if activity:
            pullables = pullables.filter(activity=activity)
        if pullables.count() > 0:
            log.debug('anybody\'s workitems: %s', str(pullables))
            query.extend(list(pullables))
        
        return query
    
    def notify_if_needed(self, user=None, roles=None):
        ''' notify user if conditions are fullfilled
        '''
        if user:
            workitems = self.list_safe(user=user, notstatus='complete', noauto=True)
            UserProfile.objects.get_or_create(user=user)
            profile = user.get_profile()
            if len(workitems) >= profile.nb_wi_notif:
                try:
                    if profile.check_notif_to_send():
                        send_mail(workitems=workitems, user=user, subject='message', template='mail.txt')
                        profile.notif_sent()
                        log.info('notification sent to %s' % user.username)
                except Exception, v:
                    log.error('sendmail error: %s' % v)
        return


class WorkItem(models.Model):
    """A workitem object represents an activity you are performing.
    
    An Activity object defines the activity, while the workitem object
    represents that you are performing this activity. So workitem is
    an "instance" of the activity.
    """
    STATUS_CHOICES = (
                      ('blocked', 'blocked'),
                      ('inactive', 'inactive'),
                      ('active', 'active'),
                      ('suspended', 'suspended'),
                      ('fallout', 'fallout'),
                      ('complete', 'complete'),
                      )
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='workitems', null=True, blank=True)
    instance = models.ForeignKey(ProcessInstance, related_name='workitems')
    activity = models.ForeignKey(Activity, related_name='workitems')
    workitem_from = models.ForeignKey('self', related_name='workitems_to', null=True, blank=True)
    others_workitems_from = models.ManyToManyField('self', related_name='others_workitems_to', null=True, blank=True)
    push_roles = models.ManyToManyField(Group, related_name='push_workitems', null=True, blank=True)
    pull_roles = models.ManyToManyField(Group, related_name='pull_workitems', null=True, blank=True)
    blocked = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')

    objects = WorkItemManager()
    
    def forward(self, timeout_forwarding=False, subflow_workitem=None):
        # forward_workitem(workitem, path=None, timeout_forwarding=False, subflow_workitem=None):
        '''
        Convenience procedure to forwards workitems to valid destination activities.
        
        @type path: string??
        @param path: XXX TODO: This is not used, so don't know why it's here.
        @type timeoutForwarding: bool
        @param timeoutForwarding:
        @type: subflow_workitem: WorkItem
        @param subflow_workitem: a workitem associated with a subflow ???
        
        '''
        log.info(u'forward_workitem %s', self.__unicode__())
        if not timeout_forwarding:
            if self.status != 'complete':
                return
        if self.has_workitems_to() and not subflow_workitem:
            log.debug('forward_workitem canceled for %s: ' 
                       'workitem.has_workitems_to()', self.__unicode__())
            return
        
        if timeout_forwarding:
            log.info('timeout forwarding')
            Event.objects.create(name='timeout', workitem=self)
        
        for destination in self.get_destinations(timeout_forwarding):
            self._forward_workitem_to_activity(destination)
            if self.activity.split_mode == 'xor': break

    def _forward_workitem_to_activity(self, target_activity):
        '''
        Passes the process instance embedded in the given workitem 
        to a new workitem that is associated with the destination activity.
        
        @type target_activity: Activity
        @param target_activity: the activity instance to which the workitem 
                                should be forwarded
        @rtype: WorkItem
        @return: a workitem that has been passed on to the next 
                 activity (and next user)
        '''
        instance = self.instance
        # search a blocked workitem first
        qwi = WorkItem.objects.filter(instance=instance, activity=target_activity, status='blocked')
        if qwi.count() == 0:
            wi = WorkItem.objects.create(instance=instance, activity=target_activity,
                                         user=None, priority=self.priority)
            created = True
            log.info('forwarded to %s', target_activity.title)
            Event.objects.create(name='creation by %s' % self.user.username, workitem=wi)
            Event.objects.create(name='forwarded to %s' % target_activity.title, workitem=self)
            wi.workitem_from = self
        else:
            created = False
            wi = qwi[0]
        
        if target_activity.join_mode == 'and':
            nb_input_transitions = target_activity.nb_input_transitions()
            if nb_input_transitions > 1:
                if created:
                    # first worktem: block it
                    wi.block()
                    return    
                else:
                    wi.others_workitems_from.add(self)
                    if wi.others_workitems_from.all().count() + 1 < nb_input_transitions:
                        # keep blocked
                        return
                    else:
                        # check if the join is OK
                        if wi.check_join():
                            wi.status = 'inactive'
                            wi.save()
                            log.info('activity %s: workitem %s unblocked', target_activity.title, str(wi))
                        else:
                            return
        else:
            if not created:
                # join_mode='and'
                log.error('activity %s: join_mode must be and', target_activity.title)
                self.fall_out()
                wi.fall_out()
                return
        
        if target_activity.autostart:
            log.info('run auto activity %s workitem %s', target_activity.title, str(wi))
            try:
                auto_user = User.objects.get(username=settings.WF_USER_AUTO)
            except Exception:
                error = 'a user named %s (settings.WF_USER_AUTO) must be defined for auto activities'
                raise Exception(error % settings.WF_USER_AUTO)
            wi.activate(actor=auto_user)
            if wi.exec_auto_application():
                wi.complete(actor=auto_user)
            return wi
        
        if target_activity.push_application:
            target_user = wi.exec_push_application()
            log.info('application pushed to user %s', target_user.username)
            wi.user = target_user
            wi.save()
            Event.objects.create(name='assigned to %s' % target_user.username, workitem=wi)
            WorkItem.objects.notify_if_needed(user=target_user)
        else:
            wi.pull_roles = wi.activity.roles.all()
            wi.save()
            WorkItem.objects.notify_if_needed(roles=wi.pull_roles)
        return wi
    
    def check_join(self):
        log.warning('workitem check_join NYI- useful ?')
        return True
    
    def _check(self, user, status=('inactive','active')):
        '''
        helper function to determine whether process is:
            - enabled, etc..
        
        '''
        if type(status)==type(''):
            status = (status,)
            
        if not self.activity.process.enabled:
            error = 'process %s disabled.' % self.activity.process.title
            log.error('workitem._check: %s' % error)
            raise Exception(error)
            
        if not self.check_user(user):
            error = 'user %s cannot take workitem %d.' % (user.username, self.pk)
            log.error('workitem._check: %s' % error)
            self.fall_out()
            raise Exception(error)
            
        if not self.status in status:
            error = 'workitem %d has not a correct status (%s/%s).' % (
                self.pk, self.status, str(status))
            log.error('workitem._check: %s' % error)
            raise Exception(error)
        return
    
    def get_destinations(self, timeout_forwarding=False):
        #get_destinations(workitem, path=None, timeout_forwarding=False):
        '''
        Return list of destination activities that meet the conditions of each transition
        
        @type path: string??
        @param path: XXX TODO: This is not used, so don't know why it's here.
        @type timeout_forwarding: bool
        @param timeout_forwarding: a workitem with a time-delay??
        @rtype: [Activity]
        @return: list of destination activities.
        '''
        transitions = Transition.objects.filter(input=self.activity)
        if timeout_forwarding:
            transitions = transitions.filter(condition__contains='workitem.time_out')
        destinations = []
        for t in transitions:
            if self.eval_transition_condition(t):
                destinations.append(t.output)
        return destinations
    
    def eval_transition_condition(self, transition):
        '''
        evaluate the condition of a transition
        '''
        if not transition.condition:
            return True
        instance = self.instance
        wfobject = instance.wfobject()
        log.debug('eval_transition_condition %s - %s', 
            transition.condition, instance.condition)
        try:
            result = eval(transition.condition)
            
            # boolean expr
            if type(result) == type(True):
                log.debug('eval_transition_condition boolean %s', str(result))
                return result
            if type(result) == type(''):
                log.debug('eval_transition_condition cmp instance.condition %s', str(instance.condition==result))
                return (instance.condition==result)
        except Exception, v:
            log.debug('eval_transition_condition [%s]: %s', transition.condition, v)
            return (instance.condition==transition.condition)
            #log.error('eval_transition_condition [%s]: %s', transition.condition, v)
        return False
    
    def exec_push_application(self):
        '''
        Execute push application in workitem
        '''
        if not self.activity.process.enabled:
            raise Exception('process %s disabled.' % self.activity.process.title)
        params = self.activity.pushapp_param
        try:
            if params: kwargs = eval(params)
            else: kwargs = {}
            result = self.activity.push_application.execute(self, **kwargs)
        except Exception, v:
            log.error('exec_push_application %s', v)
            result = None
            self.fall_out()
        return result
    
    def exec_auto_application(self):
        '''
        creates a test auto application for activities that don't yet have applications
        @rtype: bool
        '''
        try:
            if not self.activity.process.enabled:
                raise Exception('process %s disabled.' % workitem.activity.process.title)
            # no application: default auto app
            if not self.activity.application:
                return self.default_auto_app()
            
            func, args, kwargs = resolve(self.activity.application.get_app_url())
            params = self.activity.app_param
            # params values defined in activity override those defined in urls.py
            if params:
                params = eval('{'+params.lstrip('{').rstrip('}')+'}')
                kwargs.update(params)
            func(workitem=self , **kwargs)
            return True
        except Exception, v:
            log.error('execution wi %s:%s', self, v)
        return False
    
    def default_auto_app(self):
        '''
        retrieves wfobject, logs info to it saves
        
        @rtype: bool
        @return: always returns True
        '''
        obj = self.instance.wfobject()
        obj.history += '\n>>> execute auto activity: [%s]' % self.activity.title
        obj.save()
        return True
    
    def activate(self, actor):
        '''
        changes workitem status to 'active' and logs event, activator
        
        '''
        self._check(actor, ('inactive', 'active'))
        if self.status == 'active':
            log.warning('activate_workitem actor %s workitem %s already active', 
                        actor.username, str(self))
            return
        self.status = 'active'
        self.user = actor
        self.save()
        log.info('activate_workitem actor %s workitem %s', 
                 actor.username, str(self))
        Event.objects.create(name='activated by %s' % actor.username, workitem=self)
    
    def complete(self, actor):
        '''
        changes status of workitem to 'complete' and logs event
        '''
        self._check(actor, 'active')
        self.status = 'complete'
        self.user = actor
        self.save()
        log.info('complete_workitem actor %s workitem %s', actor.username, str(self))
        Event.objects.create(name='completed by %s' % actor.username, workitem=self)
        
        if self.activity.autofinish:
            log.debug('activity autofinish: forward')
            self.forward()
        
        # if end activity, instance is complete
        if self.instance.process.end == self.activity:
            log.info('activity end process %s' % self.instance.process.title)
            # first test subflow
            lwi = WorkItem.objects.filter(activity__subflow=self.instance.process,
                                          status='blocked',
                                          instance=self.instance)
            if lwi.count() > 0:
                log.info('parent process for subflow %s' % self.instance.process.title)
                workitem0 = lwi[0]
                workitem0.instance.process = workitem0.activity.process
                workitem0.instance.save()
                log.info('process change for instance %s' % workitem0.instance.title)
                workitem0.status = 'complete'
                workitem0.save()
                workitem0.forward(subflow_workitem=self)
            else:
                self.instance.set_status('complete')
    
    def start_subflow(self, actor=None):
        '''
        starts subflow and blocks passed in workitem
        '''
        if not actor: actor = self.user
        subflow_begin_activity = self.activity.subflow.begin
        instance = self.instance
        instance.process = self.activity.subflow
        instance.save()
        self.status = 'blocked'
        self.blocked = True
        self.save()
        
        sub_workitem = self._forward_workitem_to_activity(subflow_begin_activity)
        return sub_workitem
    
    def eval_condition(self, transition):
        '''
        evaluate the condition of a transition
        '''
        raise Exception("New API (not yet implemented)")
    
    def __str__(self):
        return str(self.pk)
    
    def __unicode__(self):
        return u'%s-%s-%s' % (self.instance.__unicode__(), self.activity.__unicode__(), str(self.pk))
    
    def has_workitems_to(self):
        b = ( self.workitems_to.count() > 0 )
        return b
    
    def check_user(self, user):
        """returns True if authorized, False if not.
        
        For dummy activities, returns always True
        """
        if self.activity.kind == 'dummy':
            return True
        
        if user and self.user and self.user != user:
            return False
        ugroups = user.groups.all()
        agroups = self.activity.roles.all()
        authorized = False
        if agroups and len(agroups) > 0:
            for g in ugroups:
                if g in agroups:
                    authorized = True
                    break
        else:
            authorized = True
        return authorized
            
    def set_user(self, user, commit=True):
        """affect user if he has a role authorized for activity.
        
        return True if authorized, False if not (workitem then falls out)
        """
        if self.check_user(user):
            self.user = user
            if commit: self.save()
            return True
        self.fallOut()
        return False
    
    def can_priority_change(self):
        '''can the user change priority.
        
        @rtype: bool
        @return: returns True if the user can change priority
        
        the user must belong to a group with "workitem.can_change_priority"  permission,
        and this group's name must be the same as the process title.
        '''
        if self.user.has_perm("workitem.can_change_priority"):
            lst = self.user.groups.filter(name=self.instance.process.title)
            if lst.count()==0 or \
               (lst[0].permissions.filter(codename='can_change_priority').count() == 0):
                return False
            return True
        return False
    
    def block(self):
        self.status = 'blocked'
        self.save()
        Event.objects.create(name='blocked', workitem=self)
    
    def fall_out(self):
        self.status = 'fallout'
        self.save()
        Event.objects.create(name='fallout', workitem=self)
        if not settings.DEBUG:
            mail_admins(subject='workflow workitem %s fall out' % str(self.pk),
                    message=u'''
The workitem [%s] was falling out.

Process:  %s
Activity: %s
instance: %s
----------------------------------
                    ''' % (
                           self.instance.process,
                           self.activity,
                           self.instance,
                           ))
    
    def html_action(self):
        label = 'action'
        if self.status == 'inactive':
            label = 'activate'
            url='activate/%d/' % self.id
        if self.status == 'active':
            label = 'complete'
            url='complete/%d/' % self.id
        if self.status == 'complete':
            return 'completed'
        return '<a href=%s>%s</a>' % (url, label)
    
    def html_action_link(self):
        if self.status == 'inactive':
            url='activate/%d/' % self.id
        if self.status == 'active':
            url='complete/%d/' % self.id
        if self.status == 'complete':
            raise Exception('no action for completed workitems')
        return url
    
    def time_out(self, delay, unit='days'):
        '''
        return True if timeout reached
          delay:    nb units
          unit: 'weeks' | 'days' | 'hours' ... (see timedelta)
        '''
        tdelta = eval('timedelta('+unit+'=delay)')
        now = datetime.now()
        return (now > (self.date + tdelta))
    
    @allow_tags
    def events_list(self):
        '''provide html link to events for a workitem in admin change list.
        @rtype: string
        @return: html href link "../event/?workitem__id__exact=[self.id]&ot=asc&o=0"
        '''
        nbevt = self.events.count()
        return '<a href=../event/?workitem__id__exact=%d&ot=asc&o=0>%d item(s)</a>' % (self.pk, nbevt)
    
    class Meta:
        permissions = (
            ("can_change_priority", "Can change priority"),
        )

class Event(models.Model):
    """Event are changes that happens on workitems.
    """
    date = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50)
    workitem = models.ForeignKey(WorkItem, related_name='events')
    
    def __unicode__(self):
        return self.name

