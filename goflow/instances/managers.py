#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import Group, User
from goflow.workflow.logger import Log; log = Log('goflow.instances.managers')

class ProcessInstanceManager(models.Manager):
    '''Custom model manager for ProcessInstance
    '''
   
    def add(self, user, title, obj_instance):
        '''
        Returns a newly saved ProcessInstance instance.
        
        :type user: User
        :param user: an instance of `django.contrib.auth.models.User`, 
                     typically retrieved through a request object.
        :type title: string
        :param title: the title of the new ProcessInstance instance.
        :type obj_instance: ContentType
        :param obj_instance: an instance of ContentType, which is typically 
                             associated with a django Model.
        :rtype: ProcessInstance
        :returns: a newly saved ProcessInstance instance.
        
        usage::
            
            instance = ProcessInstance.objects.add(user=admin, title="title", 
                                                   content_object=leaverequest1)
            
        '''
        instance = self.create(user=user, title=title, content_object=obj_instance)
        return instance
    
    def start(self, process_name, user, item, title=None):
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
        :rtype: WorkItem
        :return: a newly configured workitem sent to auto_user, 
                 a target_user, or ?? (roles).
        
        usage::
            
            wi = Process.objects.start(process_name='leave', 
                                       user=admin, item=leaverequest1)

        '''
        from models import WorkItem
        
        process = self.get(title=process_name, enabled=True)
        if not title or (title=='instance'):
            title = '%s %s' % (process_name, str(item))
        instance = self.add(user, title, item)
        instance.process = process
        # instance running
        instance.set_status('running')
        instance.save()
        
        workitem = WorkItem.objects.create(instance=instance, user=user, 
                                           activity=process.begin)
        log.event('created by ' + user.username, workitem)
        log('process:', process_name, 'user:', user.username, 'item:', item)
    
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


class WorkItemManager(models.Manager):
    '''Custom model manager for WorkItem
    '''
    def get_by(self, id, user=None, enabled_only=False, status=('inactive','active')):
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
        
            workitem = WorkItem.objects.get_by(id, user=request.user)
        
        '''
        if enabled_only:
            workitem = self.get(id=id, activity__process__enabled=True)
        else:
            workitem = self.get(id=id)
        workitem._check_all_for(user, status)
        return workitem

    def get_all_by(self, user=None, username=None, activity=None, status=None,
                      notstatus=('blocked','suspended','fallout','complete'), noauto=True):
        """
        Retrieve list of workitems (in order to display a task list for example).
        
        :type user: User
        :param user: filter on instance of django.contrib.auth.models.User (default=all) 
        :type username: string
        :param username: filter on username of django.contrib.auth.models.User (default=all) 
        :type activity: Activity
        :param activity: filter on instance of goflow.workflow.models.Activity (default=all) 
        :type status: string
        :param status: filter on status (default=all) 
        :type notstatus: string or tuple
        :param notstatus: list of status to exclude (default: [blocked, suspended, fallout, complete])
        :type noauto: bool
        :param noauto: if True (default) auto activities are excluded.
        
        usage::
        
            workitems = WorkItem.objects.get_all_by(user=me, notstatus='complete', noauto=True)
        
        """
        groups = Group.objects.all()
        if user:
            query = self.filter(user=user, activity__process__enabled=True)
            groups = user.groups.all()
        else:
            if username:
                query = self.filter(
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
                query = query.exclude(status=notstatus)
            else:
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
            pullables = self.filter(pull_roles=role, activity__process__enabled=True)
            if status:
                pullables = pullables.filter(status=status)
            
            if notstatus:
                pullables = pullables.exclude(status=notstatus)
            else:
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
            
            log.debug('pullables workitems role %s: %s', role, str(pullables))
            query.extend(list(pullables))
        
        return query
