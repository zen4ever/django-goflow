#!/usr/local/bin/python
# -*- coding: utf-8 -*-

def checkstatus_auto(request, workitem=None, notif_user=False):
    # print workitem
    workitem.instance.condition = 'OK: Forward to supervisor'
    return True