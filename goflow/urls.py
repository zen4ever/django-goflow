from django.conf.urls.defaults import *
from django.conf import settings
from instances.forms import DefaultAppStartForm

urlpatterns = patterns('',
    (r'^$',          'goflow.workflow.views.index', {'template':'workflow/index.html'}),
    (r'^mywork/$', 'goflow.instances.views.mywork', {'template':'mywork.html'}),
    (r'^otherswork/$', 'goflow.instances.views.otherswork', {'template':'otherswork.html'}),
    (r'^otherswork/instancehistory/$', 'goflow.instances.views.instancehistory', {'template':'instancehistory.html'}),
    (r'^myrequests/$', 'goflow.instances.views.myrequests', {'template':'myrequests.html'}),
    (r'^myrequests/instancehistory/$', 'goflow.instances.views.instancehistory', {'template':'instancehistory.html'}),
    (r'^mywork/activate/(?P<id>.*)/$', 'goflow.instances.views.activate'),
    (r'^mywork/complete/(?P<id>.*)/$', 'goflow.instances.views.complete'),
    #
    (r'^process/dot/(?P<id>.*)$','goflow.workflow.views.process_dot', {'template':'process.dot'}),
    #
    (r'^default_app/(?P<id>.*)/$', 'goflow.workflow.applications.default_app', {'template':'default_app.html'}),
    #
    (r'^.*/logout/$', 'django.contrib.auth.views.logout'),
    (r'^.*/accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'login.html'}),
    #
    (r'^start/(?P<app_label>.*)/(?P<model_name>.*)/$', 'goflow.workflow.applications.start_application'),
    (r'^start_proto/(?P<process_name>.*)/$', 'goflow.workflow.applications.start_application', {'form_class':DefaultAppStartForm, 'template':'start_proto.html'}),
    (r'^cron/$','goflow.workflow.views.cron'),
    # graphics
    (r'^graph/(?P<id>.*)/save/$', 'goflow.graphics.views.graph_save'),
    (r'^graph/(?P<id>.*)/$', 'goflow.graphics.views.graph', {'template':'graph.html'}),
)
