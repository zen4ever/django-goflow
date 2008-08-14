from django.conf.urls.defaults import *
import forms
import views

urlpatterns = patterns('goflow.apptools.views',
    # starting application
    (r'^start/$', 'start_application', {'process_name':'Sample process',
                                        'form_class':forms.SampleModelForm,
                                        'template':'start.html'}),
    # applications
    (r'^sample_choice/(?P<id>\d+)/$', 'view_object'),
    (r'^sample_view/(?P<id>\d+)/$', 'view_application'),
    (r'^sample_edit/(?P<id>\d+)/$', 'view_application'),
)

urlpatterns += patterns('',
    (r'^sample_myview/$', views.myview),
)
