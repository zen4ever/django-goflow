from django.conf.urls.defaults import *

urlpatterns = patterns('goflow.apptools.views',
    (r'^icon/image_update/$', 'image_update'),
    (r'^application/testenv/(?P<action>create|remove)/(?P<id>.*)/$', 'app_env'),
    (r'^application/teststart/(?P<id>.*)/$', 'test_start'),
)
