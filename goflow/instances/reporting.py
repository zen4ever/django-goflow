#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import WorkItem, ProcessInstance

class ActivityState:
    blocked = 0
    inactive = 0
    active = 0
    suspended = 0
    fallout = 0
    complete = 0
    total = 0
    def __init__(self, activity):
        wis = WorkItems.objects.filter(activity=activity)
        self.total = wis.count()
        self.blocked = wis.filter(status='blocked').count()
        self.inactive = wis.filter(status='inactive').count()
        self.active = wis.filter(status='active').count()
        self.fallout = wis.filter(status='fallout').count()
        self.complete = wis.filter(status='complete').count()

class ProcessState:
    initiated = 0
    running = 0
    active = 0
    complete = 0
    terminated = 0
    suspended = 0
    total = 0
    def __init__(self, process):
        insts = ProcessInstance.objects.filter(process=process)
        self.total = insts.count()
        self.initiated = insts.filter(status='initiated').count()
        self.running = insts.filter(status='running').count()
        self.active = insts.filter(status='active').count()
        self.complete = insts.filter(status='complete').count()
        self.terminated = insts.filter(status='terminated').count()
        self.suspended = insts.filter(status='suspended').count()

class ActivityStats:
    number = 0
    time_min = None
    time_max = None
    time_mean = None
    def __init__(self, activity, user=None, year=None, month=None, day=None, datetime_interval=None):
        pass
