from django.conf.urls.defaults import *
import forms

urlpatterns = patterns('goflow.apptools.views',
    (r'^start/(?P<app_label>.*)/(?P<model_name>.*)/$', 'start_application'),
    (r'^start_proto/(?P<process_name>.*)/$', 'start_application', {'form_class':forms.DefaultAppStartForm, 'template':'goflow/start_proto.html'}),
    (r'^view_application/(?P<id>\d+)/$', 'view_application'),
    (r'^view_object/(?P<id>\d+)/$', 'view_object'),
    (r'^view_object/(?P<id>\d+)/(?P<action>.*)/$', 'view_object'),
    (r'^sendmail/$', 'sendmail'),
)
