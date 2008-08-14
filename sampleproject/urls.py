from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # FOR DEBUG AND TEST ONLY
    (r'^.*switch/(?P<username>.*)/(?P<password>.*)/$', 'goflow.workflow.views.debug_switch_user'),
    # home page
    (r'^$', 'ressource.management.views.home'),
    # home redirection
    (r'^.*home/$', 'django.views.generic.simple.redirect_to', {'url':'/'}),
    # login/logout
    (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name':'logged_out.html'}),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'goflow/login.html'}),
    # Example:
    (r'^sampleapp/', include('sampleproject.sampleapp.urls')),

    # Uncomment the next line to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line for to enable the admin:
    (r'^admin/(.*)', admin.site.root),
    # workflow pages
    (r'^workflow/', include('goflow.urls')),
    # static files
    (r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
