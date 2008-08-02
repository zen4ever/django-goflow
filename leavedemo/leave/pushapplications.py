#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import Manager
from goflow.workflow.logger import Log; log = Log('leavedemo.leave.pushapplications')


def route_to_secretary(workitem):
    user = workitem.instance.user
    mgr_secretary = Manager.objects.get(category='secretary', users=user)
    return mgr_secretary.user

def route_to_supervisor(workitem):
    user = workitem.instance.user
    mgr_supervisor = Manager.objects.get(category='supervisor', users=user)
    log.debug('route_to_supervisor user %s supervisor %s',user, mgr_supervisor.user)
    return mgr_supervisor.user

