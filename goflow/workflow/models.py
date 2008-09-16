#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import resolve

from django.conf import settings

from django import forms
from decorators import allow_tags

from datetime import datetime, timedelta
from logger import Log; log = Log('goflow.workflow.managers')

class Activity(models.Model):
    """Activities represent any kind of action an employee might want to do on an instance.
    
    The action might want to change the object instance, or simply
    route the instance on a given path. Activities are the places
    where any of these action are resolved by employees.
    """
    KIND_CHOICES = (
                    ('standard', 'standard'),
                    ('dummy', 'dummy'),
                    ('subflow', 'subflow'),
                    )
    COMP_CHOICES = (
                    ('and', 'and'),
                    ('xor', 'xor'),
                    )
    title = models.CharField(max_length=100)
    kind =  models.CharField(max_length=10, choices=KIND_CHOICES, verbose_name='type', default='standard')
    process = models.ForeignKey('Process', related_name='activities')
    push_application = models.ForeignKey('PushApplication', related_name='push_activities', null=True, blank=True)
    pushapp_param = models.CharField(max_length=100, null=True, blank=True, 
                                help_text="parameters dictionary; example: {'username':'john'}")
    application = models.ForeignKey('Application', related_name='activities', null=True, blank=True,
                                help_text='leave it blank for prototyping the process without coding')
    app_param = models.CharField(max_length=100, verbose_name='parameters', 
                                 help_text='parameters dictionary', null=True, blank=True)
    subflow = models.ForeignKey('Process', related_name='parent_activities', null=True, blank=True)
    roles = models.ManyToManyField(Group, related_name='activities', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    autostart = models.BooleanField(default=False)
    autofinish = models.BooleanField(default=True)
    join_mode =  models.CharField(max_length=3, choices=COMP_CHOICES, verbose_name='join mode', default='xor')
    split_mode =  models.CharField(max_length=3, choices=COMP_CHOICES, verbose_name='split mode', default='and')
    
    def nb_input_transitions(self):
        ''' returns the number of inputing transitions.
        '''
        return Transition.objects.filter(output=self, process=self.process).count()
    
    def __unicode__(self):
        return '%s (%s)' % (self.title, self.process.title)
    
    class Meta:
        unique_together = (("title", "process"),)
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'


class ProcessManager(models.Manager):
    '''Custom model manager for Process
    '''
    
    #TODO: also not too happy about this one.
    def is_enabled(self, title):
        '''
        Determines given a title if a process is enabled or otherwise
        
        :rtype: bool
        
        usage::
        
            if Process.objects.is_enabled('leave1'):
                # do something
        
        '''
        return self.get(title=title).enabled
    
    def check_can_start(self, process_name, user):
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
        if not self.is_enabled(process_name):
            raise Exception('process %s disabled.' % process_name)
        
        if user.has_perm("workflow.can_instantiate"):
            lst = user.groups.filter(name=process_name)
            if lst.count()==0 or \
               (lst[0].permissions.filter(codename='can_instantiate').count() == 0):
                raise Exception('permission needed to instantiate process %s.' % process_name)
        else:
            raise Exception('permission needed.')
        return


class Process(models.Model):
    """A process holds the map that describes the flow of work.
    
    The process map is made of activities and transitions.
    The instances you create on the map will begin the flow in
    the configured begin activity. Instances can be moved
    forward from activity to activity, going through transitions,
    until they reach the End activity.
    """
    enabled = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    description.allow_tags=True
    begin = models.ForeignKey('Activity', related_name='bprocess', verbose_name='initial activity', null=True, blank=True)
    end = models.ForeignKey('Activity', related_name='eprocess', verbose_name='final activity', null=True, blank=True,
                            help_text='a default end activity will be created if blank')
    priority = models.IntegerField(default=0)
        
    # add new ProcessManager
    objects = ProcessManager()
    
    class Meta:
        verbose_name_plural = 'Processes'
        permissions = (
            ("can_instantiate", "Can instantiate"),
            ("can_browse", "Can browse"),
        )
    
    def __unicode__(self):
        return self.title
    
    @allow_tags
    def summary(self):
        return '<pre>%s</pre>' % self.description
    
    @allow_tags
    def action(self):
        return 'add <a href=../activity/add/>a new activity</a> or <a href=../activity/>copy</a> an activity from another process'

    
    def add_activity(self, name):
        '''
        name: name of activity (get or created)
        '''
        a, created = Activity.objects.get_or_create(title=name, process=self, 
                                                    defaults={'description':'(add description)'})
        return a 
    
    def add_transition(self, name, activity_out, activity_in):
        t, created = Transition.objects.get_or_create(name=name, process=self,
                                             output=activity_out,
                                             defaults={'input':activity_in})
        return t
    
    def create_authorized_group_if_not_exists(self):
        g, created = Group.objects.get_or_create(name=self.title)
        if created:
            ptype = ContentType.objects.get_for_model(Process)
            cip = Permission.objects.get(content_type=ptype, codename='can_instantiate')
            g.permissions.add(cip)
        
    def save(self, no_end=False):
        models.Model.save(self)
        # instantiation group
        self.create_authorized_group_if_not_exists()
        
        if not no_end and not self.end:
            self.end = Activity.objects.create(title='End', process=self, kind='dummy', autostart=True)
            models.Model.save(self)
        try:
            if self.end and self.end.process.id != self.id:
                a = self.end
                a.id = None
                a.process = self
                a.save()
                self.end = a
                models.Model.save(self)
            if self.begin and self.begin.process.id != self.id:
                a = self.begin
                a.id = None
                a.process = self
                a.save()
                self.begin = a
                models.Model.save(self)
        except Exception:
            # admin console error ?!?
            pass
        


class Application(models.Model):
    """ An application is a python view that can be called by URL.
    
        Activities can call applications.
        A commmon prefix may be defined: see settings.WF_APPS_PREFIX
    """
    url = models.CharField(max_length=255, unique=True, help_text='relative to prefix in settings.WF_APPS_PREFIX')
    # TODO: drop abbreviations (perhaps here not so necessary to ??
    SUFF_CHOICES = (
                    ('w', 'workitem.id'),
                    ('i', 'instance.id'),
                    ('o', 'object.id'),
                    )
    suffix =  models.CharField(max_length=1, choices=SUFF_CHOICES, verbose_name='suffix', null=True, blank=True,
                               default='w', help_text='http://[host]/[settings.WF_APPS_PREFIX/][url]/[suffix]')
    detected_as_auto = None
    
    def __unicode__(self):
        return self.url
    
    def get_app_url(self, workitem=None, extern_for_user=None):
        from django.conf import settings
        path = '%s/%s/' % (settings.WF_APPS_PREFIX, self.url)
        if workitem:
            if self.suffix:
                if self.suffix == 'w': path = '%s%d/' % (path, workitem.id)
                if self.suffix == 'i': path = '%s%d/' % (path, workitem.instance.id)
                if self.suffix == 'o': path = '%s%d/' % (path, workitem.instance.content_object.id)
            else:
                path = '%s?workitem_id=%d' % (path, workitem.id) 
        if extern_for_user:
            path = 'http://%s%s' % (extern_for_user.get_profile().web_host, path)
        return path
    
    def get_handler(self):
        '''returns handler mapped to url.
        '''
        try:
            func, args, kwargs = resolve(self.get_app_url() + '0/')
            self.detected_as_auto = False
        except Exception:
            func, args, kwargs = resolve(self.get_app_url())
            self.detected_as_auto = True
        return func
    
    @allow_tags
    def documentation(self):
        doc = ''
        if self.detected_as_auto:
            doc = 'detected as auto application.<hr>'
        try:
            doc += u'<pre>%s</pre>' % self.get_handler().__doc__
        except Exception, v:
            doc += 'WARNING: the url %s is not resolved.' % self.get_app_url()
        return doc
    
    def has_test_env(self):
        if Process.objects.filter(title='test_%s' % self.url).count() > 0:
            return True
        return False
    
    def create_test_env(self, user=None):
        if self.has_test_env(): 
            return
        
        g = Group.objects.create(name='test_%s' % self.url)
        ptype = ContentType.objects.get_for_model(Process)
        cip = Permission.objects.get(content_type=ptype, codename='can_instantiate')
        g.permissions.add(cip)
        # group added to current user
        if user: 
            user.groups.add(g)

        p = Process.objects.create(title='test_%s' % self.url, description='unit test process')
        p.begin = p.end
        p.begin.autostart = False
        p.begin.title = "test_activity"
        p.begin.kind = 'standard'
        p.begin.application = self
        p.begin.description = 'test activity for application %s' % self.url
        p.begin.save()
        
        p.begin.roles.add(g)
        
        p.save()
    
    def remove_test_env(self):
        if not self.has_test_env(): return
        Process.objects.filter(title='test_%s' % self.url).delete()
        Group.objects.filter(name='test_%s' % self.url).delete()
    
    @allow_tags
    def test(self):
        if self.has_test_env():
            return ('<a href=teststart/%d/>start test instances</a> | '
                    '<a href=testenv/remove/%d/>remove unit test env</a>') % (self.id, self.id)
        else:
            return '<a href=testenv/create/%d/>create unit test env</a>' % self.id



class PushApplication(models.Model):
    """A push application routes a workitem to a specific user.
    It is a python function with the same prototype as the built-in
    one below::
    
        def route_to_requester(workitem):
            return workitem.instance.user
    
    Other parameters may be added (see Activity.pushapp_param field).
    Built-in push applications are implemented in pushapps module.
    A commmon prefix may be defined: see settings.WF_PUSH_APPS_PREFIX
    
    """
    url = models.CharField(max_length=255, unique=True)
    
    def get_handler(self):
        '''returns handler mapped to url.
        '''
        try:
            # search first in pre-built handlers
            import pushapps
            if self.url in dir(pushapps):
                # TODO
                return eval('pushapps.%s' % self.url)
            # then search elsewhere
            prefix = settings.WF_PUSH_APPS_PREFIX
            # dyn import
            exec 'import %s' % prefix
            return eval('%s.%s' % (prefix, self.url))
        except Exception, v:
            log.error('PushApplication.get_handler %s', v)
        return None
    
    @allow_tags
    def documentation(self):
        return u'<pre>%s</pre>' % self.get_handler().__doc__
        
    def execute(self, workitem, **kwargs):
        handler = self.get_handler()
        return handler(workitem, **kwargs)
    
    def __unicode__(self):
        return self.url
    
    @allow_tags
    def test(self):
        return '<a href=#>test (not yet implemented)</a>'
    




   
class Transition(models.Model):
    """ A Transition connects two Activities: a From and a To activity.
    
    Since the transition is oriented you can think at it as being a
    link starting from the From and ending in the To activity.
    Linking the activities in your process you will be able to draw
    the map.
    
    Each transition is associated to a condition that will be tested
    each time an instance has to choose which path to follow.
    If the only transition whose condition is evaluated to true will
    be the transition choosen for the forwarding of the instance.
    """
    name = models.CharField(max_length=50, null=True, blank=True)
    process = models.ForeignKey(Process, related_name='transitions')
    input = models.ForeignKey(Activity, related_name='transition_inputs')
    condition = models.CharField(max_length=200, null=True, blank=True,
                                 help_text='ex: instance.condition=="OK" | OK')
    output = models.ForeignKey(Activity, related_name='transition_outputs')
    description = models.CharField(max_length=100, null=True, blank=True)
    precondition = models.SlugField(null=True, blank=True, help_text='object method that return True if transition is posible')
    
    def is_transition(self):
        ''' used in admin templates.
        '''
        return True
    
    def save(self):
        if self.input.process != self.process or self.output.process != self.process:
            raise Exception("a transition and its activities must be linked to the same process")
        models.Model.save(self)
    
    def __unicode__(self):
        return self.name or 't%s' % str(self.pk)

    class Meta:
        pass
        #unique_together = (("input", "condition"),)


class UserProfile(models.Model):
    """Contains workflow-specific user data.
    
    It has to be declared as auth profile module as following:
    settings.AUTH_PROFILE_MODULE = 'workflow.userprofile'
    
    If your application have its own profile module, you must
    add to it the workflow.UserProfile fields.
    """
    user = models.ForeignKey(User, unique=True)
    web_host = models.CharField(max_length=100, default='localhost:8000')
    notified = models.BooleanField(default=True, verbose_name='notification by email')
    last_notif = models.DateTimeField(default=datetime.now())
    nb_wi_notif = models.IntegerField(default=1, verbose_name='items before notification', 
                                      help_text='notification if the number of items waiting is reached')

    notif_delay = models.IntegerField(default=1, verbose_name='Notification delay', help_text='in days')
    urgent_priority = models.IntegerField(default=5, verbose_name='Urgent priority threshold', help_text='a mail notification is sent when an item has at least this priority level')
    
    def save(self, **kwargs):
        if not self.last_notif: self.last_notif = datetime.now()
        models.Model.save(self,  **kwargs)
    
    def check_notif_to_send(self):
        now = datetime.now()
        if now > self.last_notif + timedelta(days=self.notif_delay or 1):
            return True
        return False
    
    def notif_sent(self):
        now = datetime.now()
        self.last_notif = now
        self.save()

    class Meta:
        verbose_name='Workflow user profile'
        verbose_name_plural='Workflow users profiles'

