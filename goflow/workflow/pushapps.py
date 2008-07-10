#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
import logging
_logger = logging.getLogger('workflow.log')

def route_to_requester(workitem):
    return workitem.instance.user

def route_to_superuser(workitem, username='admin'):
    user = User.objects.get(username=username)
    if user.is_superuser(): return user
    _logger.warning('this user is not a super-user:', username)
    return None

def to_current_superuser(workitem, user_pushed):
    ''' NYI
    should be used in all push applications for testing purposes:
      usage:
        ....
        return to_current_superuser(workitem, user_pushed)
    '''
    return None

def route_to_user(workitem, username):
    return User.objects.get(username=username)
