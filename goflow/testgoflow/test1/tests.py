#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import unittest
from django.test.client import Client
from django.core import mail
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from goflow.instances.models import DefaultAppModel
from goflow.workflow.models import *
from goflow.instances.models import *
from goflow.workflow.api import *


class Test(unittest.TestCase):
    def test_access_object_from_instance(self):
        user = User.objects.get(username='userA')
        inst = DefaultAppModel.objects.create(comment='test_access_object_from_instance')
        instance = add_instance(user, "test_instance", inst)
        self.assertEquals(inst, instance.wfobject(), "get object with instance.wfobject()")
    
    def test_connect_admin(self):
        client = Client()
        ok = client.login(username='userA', password='a')
        
        response = client.get('/admin/')
        self.failUnlessEqual(response.status_code, 200)
        client.logout()
    
    def test_notif(self):
        user = User.objects.get(username='userA')
        
        profile = user.get_profile() # userprofile_set.all()[0]
        profile.last_notif = datetime.now()
        profile.delai_notif = 1
        profile.save()
        
        mail.outbox = []
        model = DefaultAppModel.objects.create(comment='test_notif')
        workitem = start_instance('test2', user, model)
        notify_if_needed(user)
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 0)
        
        profile.last_notif = datetime.now() - timedelta(days=2)
        profile.save()
        notify_if_needed(user)
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        
    def test_push_apps(self):
        user = User.objects.get(username='userA')
        workitem = start_instance('test2', user, DefaultAppModel.objects.create(comment='test_notif'))
        workitem.activity.push_application.url = 'route_to_user'
        workitem.activity.pushapp_param = "{'username':'any'}"
        exec_push_application(workitem)
    
    def test_forwd_nopush(self):
        user = User.objects.get(username='any')
        workitem = start_instance('question_process', user, DefaultAppModel.objects.create(comment='test'))
        
        workitem.activity = Activity.objects.get(title='answer question')
        workitem.user = None
        workitem.save()
        B = Group.objects.get(name='B')
        workitem.pullRoles.add(B)
        user.groups.add(B)
        lwi = get_workitems(user=user, notstatus='c', noauto=True)
        self.assertEquals(workitem, lwi[0], "user with role B has access to workitem")
        return
        
    def test_process_save(self):
        p = Process.objects.get(id=3)
        p.save()
    
    def test_change_obinstance(self):
        user = User.objects.get(username='any')
        workitem = start_instance('question_process', user, DefaultAppModel.objects.create(comment='test'))
        instance = workitem.instance
        ob = instance.wfobject()
        changeObjectInstance(instance, DefaultAppModel.objects.create(comment='test 2'))
        instance = ProcessInstance.objects.get(id=instance.id)
        self.assertNotEquals(instance.wfobject(), ob, "instance object has changed")
          