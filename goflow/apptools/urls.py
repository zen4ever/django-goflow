from django.conf.urls.defaults import *
import views
import forms

urlpatterns = patterns('',
    (r'^start/(?P<app_label>.*)/(?P<model_name>.*)/$', 'goflow.apptools.views.start_application'),
    (r'^start_proto/(?P<process_name>.*)/$', 'goflow.apptools.views.start_application', {'form_class':forms.DefaultAppStartForm, 'template':'goflow/start_proto.html'}),
)
