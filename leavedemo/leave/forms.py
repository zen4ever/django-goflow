#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import LeaveRequest

from goflow.apptools.forms import BaseForm, StartForm

# allows calendar widgets
from django import forms

class StartRequestForm(StartForm):
    day_start = forms.DateField(widget=forms.TextInput(attrs={'class': 'vDateField'}))
    day_end = forms.DateField(widget=forms.TextInput(attrs={'class': 'vDateField'}))
    
    def save(self, user, data=None, commit=True):
        ''' overriden for adding the requester
        '''
        obj = super(StartForm, self).save(commit=False)
        obj.requester = user
        obj.save()
        return obj
    
    class Meta:
         model = LeaveRequest
         exclude = ('reason_denial', 'requester')

class RequesterForm(BaseForm):
    class Meta:
         model = LeaveRequest
         exclude = ('reason_denial', 'requester')

class CheckRequestForm(BaseForm):
    class Meta:
         model = LeaveRequest
         fields = ('reason_denial',)

