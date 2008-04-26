from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^application/testenv/(?P<action>create|remove)/(?P<id>.*)/$', 'goflow.workflow.views.app_env'),
    (r'^application/teststart/(?P<id>.*)/$', 'goflow.workflow.views.test_start'),
)
