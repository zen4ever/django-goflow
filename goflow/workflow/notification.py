#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import logger, logging
_logger = logging.getLogger('workflow.log')
from models import UserProfile
from datetime import datetime, timedelta

def notify_if_needed(user=None, roles=None):
    ''' notify user if conditions are fullfilled
    '''
    from api import get_workitems
    if user:
        workitems = get_workitems(user=user, notstatus='c', noauto=True)
        UserProfile.objects.get_or_create(user=user)
        profile = user.get_profile()
        if len(workitems) >= profile.nb_wi_notif:
            try:
                if profile.check_notif_to_send():
                    send_mail(workitems=workitems, user=user, subject='message', template='mail.txt')
                    profile.notif_sent()
                    _logger.info('notification sent to %s' % user.username)
            except Exception, v:
                _logger.error('sendmail error: %s' % v)
    return
            

from django.template import Context, Template
from django.template.loader import render_to_string
def send_mail(workitems=None, user=None, subject='message', template='mail.txt'):
    # subject
    try:
        subject = settings.EMAIL_SUBJECT_PREFIX + subject
    except Exception:
        pass
    t = Template(subject)
    subject = t.render(Context({'workitems': workitems,'user':user}))
    profile = user.get_profile()
    message = render_to_string(template, {
                                          'workitems': workitems,
                                          'user':user,
                                          'url_prefix':'http://%s/' % profile.web_host
                                          })
    
    user.email_user(subject, message)
