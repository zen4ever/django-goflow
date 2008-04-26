#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from goflow.workflow.models import Process, Activity

class ProcessImage(models.Model):
    process = models.ForeignKey(Process)
    file = models.ImageField(upload_to='images')
    
    def graphic(self):
        return '<img name=image%d src=%s>' % (self.id, self.get_file_url())
    graphic.allow_tags=True
    def graphic_input(self):
        return '<input type=image name=process src=%s>' % self.get_file_url()
    graphic_input.allow_tags=True
    
    def list_activities(self):
        return self.process.activities.all()
    
    def list_activity_positions(self):
        return ActivityPosition.objects.filter(diagram=self)
    
    class Admin:
        list_display = ('process', 'graphic', 'file')
    def __unicode__(self):
        return self.process.title

class ActivityPosition(models.Model):
    diagram = models.ForeignKey(ProcessImage)
    activity = models.ForeignKey(Activity)
    x = models.PositiveSmallIntegerField(default=0)
    y = models.PositiveSmallIntegerField(default=0)
    class Admin:
        list_display = ('activity', 'diagram', 'x', 'y')
