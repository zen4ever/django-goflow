#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models


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
