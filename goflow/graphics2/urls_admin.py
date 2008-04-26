from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^processimage/pos_activity/$', 'goflow.graphics2.views.pos_activity'),
)
