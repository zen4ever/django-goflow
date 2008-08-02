#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django import forms
from django.contrib.contenttypes.models import ContentType

ctypes = ContentType.objects.\
        exclude(app_label='auth').\
        exclude(app_label='contenttypes').\
        exclude(app_label='workflow').\
        exclude(app_label='graphics').\
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
    
