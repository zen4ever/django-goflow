from django.conf.urls.defaults import *
from django.conf import settings
from apptools.forms import DefaultAppStartForm

urlpatterns = patterns('',
    (r'^$',          'goflow.workflow.views.index', {'template':'workflow/index.html'}),
    (r'^mywork/$', 'goflow.instances.views.mywork', {'template':'goflow/mywork.html'}),
    (r'^otherswork/$', 'goflow.instances.views.otherswork', {'template':'goflow/otherswork.html'}),
    (r'^otherswork/instancehistory/$', 'goflow.instances.views.instancehistory', {'template':'goflow/instancehistory.html'}),
    (r'^myrequests/$', 'goflow.instances.views.myrequests', {'template':'goflow/myrequests.html'}),
    (r'^myrequests/instancehistory/$', 'goflow.instances.views.instancehistory', {'template':'goflow/instancehistory.html'}),
    (r'^mywork/activate/(?P<id>.*)/$', 'goflow.instances.views.activate'),
    (r'^mywork/complete/(?P<id>.*)/$', 'goflow.instances.views.complete'),
    #
    (r'^process/dot/(?P<id>.*)$','goflow.workflow.views.process_dot', {'template':'goflow/process.dot'}),
    #
    (r'^default_app/(?P<id>.*)/$', 'goflow.apptools.views.default_app', {'template':'goflow/default_app.html'}),
    #
    (r'^.*/logout/$', 'django.contrib.auth.views.logout'),
    (r'^.*/accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'goflow/login.html'}),
    #
    (r'^start/(?P<app_label>.*)/(?P<model_name>.*)/$', 'goflow.apptools.views.start_application'),
    (r'^start_proto/(?P<process_name>.*)/$', 'goflow.apptools.views.start_application', {'form_class':DefaultAppStartForm, 'template':'goflow/start_proto.html'}),
    (r'^cron/$','goflow.workflow.views.cron'),
    # app
    (r'^apptools/', include('goflow.apptools.urls')),
    # graphics
    (r'^graph/', include('goflow.graphics.urls')),
)
