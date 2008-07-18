#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from goflow.graphics2.models import ProcessImage, ActivityPosition
from goflow.workflow.models import Activity

def pos_activity(request, process_id):
    process = ProcessImage.objects.get(id=int(process_id))
    activity = Activity.objects.get(id=int(request.GET['activity']))
    activity_pos, created = ActivityPosition.objects.get_or_create(activity=activity, diagram=process)
    x = int(request.GET['process.x'])
    y = int(request.GET['process.y'])
    activity_pos.x = x
    activity_pos.y = y
    activity_pos.save()
    request.user.message_set.create(
        message='activity %s in positioned in the diagram of process %s.' % (activity.title, process.process.title)
    )
    return HttpResponseRedirect('..')