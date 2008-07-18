#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models

class ProcessInstanceManager(models.Manager):
    def add(self, user, title, obj_instance):
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
        raise Exception("New API (not yet implemented)")

class WorkItemManager(models.Manager):
    def safe_filter(self, user=None, username=None, activity=None, status=None,
                      notstatus=('blocked','suspended','fallout','complete'), noauto=True):
        """
        get workitems (in order to display a task list for example).
        
        user or username: filter on user (default=all)
        activity: filter on activity (default=all)
        status: filter on status (default=all)
        notstatus: list of status to exclude
                   (default is a list of these: blocked, suspended, fallout, complete)
        noauto: if True (default) auto activities are excluded.
        """
        raise Exception("New API (not yet implemented)")
