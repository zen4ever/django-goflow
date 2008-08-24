#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import DefaultAppModel

from django.forms import ModelForm
from django import forms
from datetime import datetime

from django.contrib.contenttypes.models import ContentType


class BaseForm(ModelForm):
    '''
    base class for edition forms
    '''
    
    workitem_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    priority = forms.ChoiceField(label=u'Priorité', widget=forms.RadioSelect, initial='0',
                                 choices=(('0','normal'), ('1','urgent'), ('5','prioritaire')),
                                 )
    def save(self, workitem=None, submit_value=None, commit=True):
        ob = super(BaseForm, self).save(commit=commit)
        if workitem and workitem.can_priority_change():
            workitem.priority = int(self.cleaned_data['priority'])
            workitem.save()
        return ob
    
    def pre_check(self, obj_context=None, user=None):
        """may be overriden to do some check before.
        
        obj_context    object instance (if cmp_attr is set, this is the root object)
        an exception should be risen if pre-conditions are not fullfilled
        """
        pass

    class Meta:
         exclude = ('workitem_id',)

class StartForm(ModelForm):
    '''
    base class for starting a workflow
    '''
    priority = forms.ChoiceField(label=u'Priorité', widget=forms.RadioSelect, initial='0',
                                 choices=(('0','normal'), ('1','urgent'), ('5','prioritaire')),
                                 )
    
    def save(self, user=None, data=None, commit=True):
        ob = super(StartForm, self).save(commit=commit)
        return ob
    
    def pre_check(self, user=None):
        """may be overriden to do some check before.
        
        an exception should be risen if pre-conditions are not fullfilled
        """
        pass


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
        ob.save()
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
        ob.save()
        return ob

    class Meta:
         model = DefaultAppModel
         exclude = ('reasonDenial',)


ctypes = ContentType.objects.\
        exclude(app_label='auth').\
        exclude(app_label='contenttypes').\
        exclude(app_label='workflow').\
        exclude(app_label='graphics').\
        exclude(app_label='graphics2').\
        exclude(app_label='runtime').\
        exclude(app_label='apptools').\
        exclude(app_label='sessions').\
        exclude(app_label='sites').\
        exclude(app_label='admin')

class ContentTypeForm(forms.Form):
    ctype = forms.ModelChoiceField(
                queryset=ctypes, 
                required=True, 
                empty_label='(select a content-type)',
                label='content type',
                help_text=('clone all instances of the selected content type and push '
                           'them in the test process of the application')
            )
    
