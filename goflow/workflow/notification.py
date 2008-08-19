#!/usr/local/bin/python
# -*- coding: utf-8 -*-

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
