#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import  os, sys
os.environ["DJANGO_SETTINGS_MODULE"]="leavedemo.settings"
_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_dir, '..'))

from goflow.workflow.api import execAutoApplication
from goflow.workflow.models import WorkItem
from goflow.workflow.views import cron
#from django.core.urlresolvers import resolve

#cron()
from django.contrib.auth.models import User
from goflow.workflow.applications import send_mail
user = User.objects.get(username='admin')
wi = WorkItem.objects.get(id=1)
send_mail(None, wi, 'admin', subject="message for {{user.username}}")
'''

wi.activity.application.url = 'send_mail'
execAutoApplication(wi)

#result = resolve('/leavedemo/checkstatus_auto/')
#print result
pass
'''