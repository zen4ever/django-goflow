#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

def push_app_userA(workitem):
    return User.objects.get(username='userA')
