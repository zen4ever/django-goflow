#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.db import models

class ProcessManager(models.Manager):
    def add(self):
        '''
        Creates, saves, and returns a Process instance
        and adds an intital activity to it.
        
        @type title: string
        @param title: the title of the new Process instance.
        @type description: string
        @param description: a short description of the new Process instance.
        @rtype: Process
        @return: a newly saved Process instance.
        '''
        raise Exception("New API (not yet implemented)")
