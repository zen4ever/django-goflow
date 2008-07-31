from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^processimage/(?P<process_id>.*)/pos_activity/$', 'goflow.graphics.views.pos_activity'),
)
