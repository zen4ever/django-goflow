#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import DefaultAppModel

from django.newforms import ModelForm
from django import newforms as forms
from datetime import datetime


class BaseForm(ModelForm):
    '''
    base class for edition forms
    '''
    workitem_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    def save(self, workitem=None, submit_value=None, commit=True):
        ob = super(BaseForm, self).save(commit=commit)
        return ob
    
    class Meta:
         exclude = ('wfinstance', 'workitem_id')

class StartForm(ModelForm):
    '''
    base class for starting a workflow
    '''
    def save(self, user=None, data=None, commit=True):
        ob = super(StartForm, self).save(commit=commit)
        return ob
    
    class Meta:
         exclude = ('wfinstance',)


class DefaultAppForm(BaseForm):
    def save(self, workitem=None, submit_value=None, commit=True):
        ob = super(DefaultAppForm, self).save(commit=False)
        if ob.comment:
            if not ob.history:
                ob.history = 'Init'
            ob.history += '\n---------'
            if workitem:
                ob.history += '\nActivity: [%s]' % workitem.activity.title
            ob.history += '\n%s\n%s' % (datetime.now().isoformat(' '), ob.comment)
            ob.comment = None
        if submit_value:
            if ob.history:
                ob.history += '\n button clicked: [%s]' % submit_value
        ob.save(self)
        return ob
    
    class Meta:
         model = DefaultAppModel
         exclude = ('reasonDenial',)


class DefaultAppStartForm(StartForm):
    def save(self,  user=None, data=None, commit=True):
        ob = super(DefaultAppStartForm, self).save(commit=False)
        if not ob.history:
            ob.history = 'Init'
        ob.history += '\n%s start instance' % datetime.now().isoformat(' ')
        if ob.comment:
            ob.history += '\n---------'
            ob.history += '\n%s' % ob.comment
            ob.comment = None
        ob.save(self)
        return ob
    
    class Meta:
         model = DefaultAppModel
         exclude = ('reasonDenial',)
