from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # django-flags for internationalization
    (r'^lang/', include('sampleproject.flags.urls')),
    # FOR DEBUG AND TEST ONLY
    (r'^.*switch/(?P<username>.*)/(?P<password>.*)/$', 'goflow.workflow.views.debug_switch_user'),
    # home page
    (r'^$', 'sampleproject.sampleapp.views.home'),
    # home redirection
    (r'^.*home/$', 'django.views.generic.simple.redirect_to', {'url':'/'}),
    # login/logout
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'goflow/login.html'}),
    # Example:
    (r'^sampleapp/', include('sampleproject.sampleapp.urls')),

    # Uncomment the next line to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # FOR TEST - insert before admin/(.*)
    (r'^admin/workflow/', include('goflow.apptools.urls_admin')),
    # special
    (r'^admin/apptools/', include('goflow.apptools.urls_admin')),
    
    # Uncomment the next line for to enable the admin:
    (r'^admin/(.*)', admin.site.root),
    # workflow pages
    (r'^workflow/', include('goflow.urls')),
    # static files
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
