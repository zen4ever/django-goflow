#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from logger import Log; log = Log('goflow.workflow.managers')

class ProcessManager(models.Manager):
    '''Custom model manager for Process
    '''
    
    def add(self):
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
        raise Exception("New API (not yet implemented)")
    
    
    #TODO: also not too happy about this one.
    def process_is_enabled(self, title):
        '''
        Determines given a title if a process is enabled or otherwise
        
        :rtype: bool
        
        usage::
        
            if Process.objects.process_is_enabled('leave1'):
                # do something
        
        '''
        return self.get(title=title).enabled

    def add(self, title, description=''):
        '''
        Creates, saves, and returns a Process instance
        and adds an intital activity to it.

        :type title: string
        :param title: the title of the new Process instance.
        :type description: string
        :param description: an optional description of the new Process instance.
        :rtype: Process
        :return: a new (saved) Process instance.
        
        usage::
            
            process1 = Process.objects.add(title='process1')
        '''
        process = self.create(title=title, description=description)
        process.begin = models.get_model('workflow', 'Activity').objects.create(
            title='initial', process=process)
        #process.end = Activity.objects.create(title='final', process=process)
        process.save()
        return process

    #TODO: not too happy with the naming or place of the function here..
    def check_start_instance_perm(self, process_name, user):
        '''
        Checks whether a process is enabled and whether the user has permission
        to instantiate it; raises exceptions if not the case, returns None otherwise.

        :type process_name: string
        :param process_name: a name of a process. e.g. 'leave'
        :type user: User
        :param user: an instance of django.contrib.auth.models.User, 
                     typically retrieved through a request object.
        :rtype:
        :return: passes silently if checks are met, 
                 raises exceptions otherwise.
        
        usage::
        
            Process.objects.check_start_instance_perm(process_name='leave1', user=admin)
    
        '''
        if not self.process_is_enabled(process_name):
            raise Exception('process %s disabled.' % process_name)

        if user.has_perm("workflow.can_instantiate"):
            lst = user.groups.filter(name=process_name)
            if lst.count()==0 or \
               (lst[0].permissions.filter(codename='can_instantiate').count() == 0):
                raise Exception('permission needed to instantiate process %s.' % process_name)
        else:
            raise Exception('permission needed.')
        return
