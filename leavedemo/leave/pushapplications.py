#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import Manager
import logging
_log = logging.getLogger('workflow.log')

def route_to_secretary(workitem):
    user = workitem.instance.user
    mgr_secretary = Manager.objects.get(category='secretary', users=user)
    return mgr_secretary.user

def route_to_supervisor(workitem):
    user = workitem.instance.user
    mgr_supervisor = Manager.objects.get(category='supervisor', users=user)
    _log.debug('route_to_supervisor user %s supervisor %s',user, mgr_supervisor.user)
    return mgr_supervisor.user

