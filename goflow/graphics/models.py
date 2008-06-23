#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Image(models.Model):
    file = models.ImageField(upload_to='images')
    info = models.CharField(max_length=100, null=True, blank=True)
    
    def graphic(self):
        return '<img name=image%d src=%s>' % (self.id, self.get_file_url())
    graphic.allow_tags=True
    
    class Admin:
        list_display = ('info', 'graphic', 'file')
    def __unicode__(self):
        return self.info

class Graph(models.Model):
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name
    class Admin:
        list_display = ('name',)

class Visual(models.Model):
    x = models.PositiveSmallIntegerField(default=0)
    y = models.PositiveSmallIntegerField(default=0)
    w = models.PositiveSmallIntegerField(default=0)
    h = models.PositiveSmallIntegerField(default=0)
    needUpdate = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    z = models.PositiveSmallIntegerField(default=0)
    image = models.ForeignKey(Image, null=True, blank=True)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    graph = models.ForeignKey(Graph)
    
    def graphic(self):
        return '<img src=%s>' % self.image.get_file_url()
    graphic.allow_tags=True
    
    class Admin:
        list_display = ('graphic', 'content_type', 'object_id', 'graph')
