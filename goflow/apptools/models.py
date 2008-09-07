#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from goflow.workflow.models import Transition
from goflow.workflow.decorators import allow_tags
from django.conf import settings


class DefaultAppModel(models.Model):
    """Default implementation object class  for process instances.
    
    When a process instance starts, the instance has to carry an
    implementation object that contains the application data. The
    specifications for the implementation class is:
    
    (nothing: now managed by generic relation)
    
    This model is used in process simulations: you don't have to define
    application in activities for this; the DefaultAppModel is used
    to keep workflow history for displaying to users.
    """
    history = models.TextField(editable=False, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return 'simulation model %s' % str(self.id)
    class Admin:
        list_display = ('__unicode__',)
    class Meta:
        verbose_name='Simulation object'

class Image(models.Model):
    category = models.CharField(max_length=20, null=True, blank=True)
    file = models.ImageField(upload_to='images')
    
    def url(self):
        return "%s%s" % (settings.MEDIA_URL, self.file)
    
    @allow_tags
    def graphic(self):
        return '<img name="image%d" src="%s">' % (self.pk, self.url())
    
    @allow_tags
    def graphic_input(self):
        return '<input type=image name=icon src=%s>' % self.get_file_url()
    
    def __unicode__(self):
        return str(self.file)

class Icon(models.Model):
    category = models.CharField(max_length=20, null=True, blank=True)
    url = models.URLField(verify_exists=False)
    
    @allow_tags
    def graphic(self):
        return '<img name="image%d" src="%s">' % (self.pk, self.url)
    
    @allow_tags
    def graphic_input(self):
        return '<input type=image name=icon src="%s">' % self.url
    
    def __unicode__(self):
        return self.url

class TransitionIcon(models.Model):
    label = models.CharField(max_length=100)
    transition = models.OneToOneField(Transition, related_name='icon')
    icon = models.ForeignKey(Icon)
    
    def is_transition_icon(self):
        ''' used in admin templates.
        '''
        return True
    
    @allow_tags
    def graphic(self):
        return '<img name="trimage%d" src="%s">' % (self.pk, self.icon.url)
    
    @allow_tags
    def graphic_input(self):
        return '<input type=image name=transition src="%s">' % self.icon.url
    
    def __unicode__(self):
        return self.label
