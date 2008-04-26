#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from models import LeaveRequest

from goflow.instances.forms import BaseForm, StartForm

class StartRequestForm(StartForm):
    class Meta:
         model = LeaveRequest
         exclude = ('reasonDenial',)

class RequesterForm(BaseForm):
    class Meta:
         model = LeaveRequest
         exclude = ('reasonDenial',)

class CheckRequestForm(BaseForm):
    class Meta:
         model = LeaveRequest
         fields = ('reasonDenial',)

