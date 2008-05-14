#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import WorkItem, Instance

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
        self.blocked = wis.filter(status='b').count()
        self.inactive = wis.filter(status='i').count()
        self.active = wis.filter(status='a').count()
        self.fallout = wis.filter(status='f').count()
        self.complete = wis.filter(status='c').count()

class ProcessState:
    initiated = 0
    running = 0
    active = 0
    complete = 0
    terminated = 0
    suspended = 0
    total = 0
    def __init__(self, process):
        insts = Instance.objects.filter(process=process)
        self.total = insts.count()
        self.initiated = insts.filter(status='i').count()
        self.running = insts.filter(status='r').count()
        self.active = insts.filter(status='a').count()
        self.complete = insts.filter(status='c').count()
        self.terminated = insts.filter(status='t').count()
        self.suspended = insts.filter(status='s').count()

class ActivityStats:
    number = 0
    time_min = None
    time_max = None
    time_mean = None
    def __init__(self, activity, user=None, year=None, month=None, day=None, datetime_interval=None):
        pass
