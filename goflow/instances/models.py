#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import Group, User
from goflow.workflow.models import Process, Activity
from datetime import timedelta, datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Instance(models.Model):
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
    
    The Instance will collect and handle workitems (see definition)
    to be passed from activity to activity in the process.
    
    Each instance can have more than one workitem depending on the
    number of split actions encountered in the process flow.
    That means that an instance is actually the collection of all of
    the instance "pieces" (workitems) that we get from splits of the
    same original process instance.
    
    Each Instance keeps track of its history through a graph.
    Each node of the graph represents an activity the instance has
    gone through (normal graph nodes) or an activity the instance is
    now pending on (a graph leaf node). Tracking the Instance history
    can be very useful for the Instance monitoring.
    
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
      wfinstances = generic.GenericRelation(Instance)
    
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
    creationTime = models.DateTimeField(auto_now_add=True, core=True)
    user = models.ForeignKey(User, related_name='instances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='initiated')
    old_status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True)
    condition = models.CharField(max_length=50, null=True, blank=True)
    
    # refactoring
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def wfobject(self):
        return self.content_object
        
    def __str__(self):
        return self.title
    
    def __unicode__(self):
        return self.title
    
    def set_status(self, status):
        if not status in [x for x,y in Instance.STATUS_CHOICES]:
            raise Exception('instance status incorrect :%s' % status)
        self.old_status = self.status
        self.status = status
        self.save()
    
    class Admin:
        date_hierarchy = 'creationTime'
        list_display = ('title', 'process', 'user', 'creationTime', 'status')
        list_filter = ('process', 'user')

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
    date = models.DateTimeField(auto_now=True, core=True)
    user = models.ForeignKey(User, related_name='workitems', null=True, blank=True)
    instance = models.ForeignKey(Instance, related_name='workitems')
    activity = models.ForeignKey(Activity, related_name='workitems')
    workitem_from = models.ForeignKey('self', related_name='workitems_to', null=True, blank=True)
    push_roles = models.ManyToManyField(Group, related_name='push_workitems', null=True, blank=True)
    pull_roles = models.ManyToManyField(Group, related_name='pull_workitems', null=True, blank=True)
    blocked = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')
        
    def __unicode__(self):
        return '%s-%s-%s' % (unicode(self.instance), self.activity, str(self.id))
    
    def has_workitems_to(self):
        b = ( self.workitems_to.count() > 0 )
        return b
    
    def check_user(self, user):
        """return True if authorized, False if not.
        """
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
    
    def fall_out(self):
        self.status = 'fallout'
        self.save()
        Event.objects.create(name='fallout', workitem=self)
    
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
        #label = 'action'
        if self.status == 'inactive':
            #label = 'activate'
            url='activate/%d/' % self.id
        if self.status == 'active':
            #label = 'complete'
            url='complete/%d/' % self.id
        if self.status == 'complete':
            raise Exception('no action for completed workitems')
        return '<a href=%s>' % (url)
    
    def time_out(self, delay, unit='days'):
        '''
        return True if timeout reached
          delay:    nb units
          unit: 'weeks' | 'days' | 'hours' ... (see timedelta)
        '''
        tdelta = eval('timedelta('+unit+'=delay)')
        now = datetime.now()
        return (now > (self.date + tdelta))
        
    class Admin:
        date_hierarchy = 'date'
        list_display = ('date', 'user', 'instance', 'activity', 'status',)
        list_filter = ('user', 'activity', 'status')

class Event(models.Model):
    """Event are changes that happens on workitems.
    """
    date = models.DateTimeField(auto_now=True, core=True)
    name = models.CharField(max_length=50, core=True)
    workitem = models.ForeignKey(WorkItem, related_name='events', edit_inline=True)
    class Admin:
        date_hierarchy = 'date'
        list_display = ('date', 'name', 'workitem')


class DefaultAppModel(models.Model):
    """Default implementation object class  for process instances.
    
    When a process instance starts, the instance has to carry an
    implementation object that contains the application data. The
    specifications for the implementation class is:
    
    (nothing: now managed by generic relation)
    
    This model is used in process simulations: you don't have to define
    application in activities for this; the DefaultAppModel is used
    to keep workflow history for displaying to users.
    """
    history = models.TextField(editable=False, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return 'simulation model %s' % str(self.id)
    class Admin:
        list_display = ('__unicode__',)
    class Meta:
        verbose_name='Simulation object'
