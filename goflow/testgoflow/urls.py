from django.conf.urls.defaults import *
from goflow.instances.forms import DefaultAppForm

urlpatterns = patterns('',
    (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '../graphics/js', 'show_indexes': False}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'images', 'show_indexes': False}),
    # FOR DEBUG AND TEST ONLY
    (r'^.*/switch/(?P<username>.*)/(?P<password>.*)/$', 'goflow.workflow.views.debug_switch_user'),
    # home applications
    (r'^test1/$', 'django.views.generic.simple.direct_to_template', {'template':'home.html'}),
    #
    (r'^.*/home/$', 'django.views.generic.simple.redirect_to', {'url':'/workflow/'}),
    # test edit_model handler
    (r'^edit/(?P<id>.*)/$', 'goflow.workflow.applications.edit_model', {'form_class':DefaultAppForm}),
    #
    (r'^admin/workflow/', include('goflow.urls_admin')),
    (r'^admin/graphics2/', include('goflow.graphics2.urls_admin')),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^workflow/', include('goflow.urls')),
)
