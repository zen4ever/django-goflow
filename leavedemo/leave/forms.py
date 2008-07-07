#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import LeaveRequest

from goflow.instances.forms import BaseForm, StartForm

class StartRequestForm(StartForm):
    def save(self, user, data=None, commit=True):
        ''' overriden for adding the requester
        '''
        ob = super(StartForm, self).save(commit=False)
        ob.requester = user
        ob.save()
        return ob
    
    class Meta:
         model = LeaveRequest
         exclude = ('reasonDenial', 'requester')

class RequesterForm(BaseForm):
    class Meta:
         model = LeaveRequest
         exclude = ('reasonDenial', 'requester')

class CheckRequestForm(BaseForm):
    class Meta:
         model = LeaveRequest
         fields = ('reasonDenial',)

