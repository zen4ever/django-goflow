from django.conf.urls.defaults import *
import forms
import views

urlpatterns = patterns('goflow.apptools.views',
    # starting application
    (r'^start/$', 'start_application', {'process_name':'Sample process',
                                        'form_class':forms.SampleModelForm,
                                        'template':'sample/start.html'}),
    # applications provided by goflow.apptools
    (r'^apptools/', include('goflow.apptools.urls')),
    # applications
    (  r'^sample_edit/(?P<id>\d+)/$', 'edit_model', {'template':  'edit.html'}),
)

urlpatterns += patterns('',
    (r'^sample_myview/$', views.myview),
)

urlpatterns += patterns('goflow.runtime.views',
    (r'^mywork/$', 'mywork', {'template':'sample/mywork.html'}),
    (r'^mywork/activate/(?P<id>.*)/$', 'activate'),
    (r'^mywork/complete/(?P<id>.*)/$', 'complete'),
)
