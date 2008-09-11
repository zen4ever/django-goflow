The Leave application
---------------------

(Obsolete ?)

This note shows how to use the GoFlow workflow engine.

Settings.py:
------------

1. Standard settings:

	INSTALLED_APPS = (
	    ....
	    'django.contrib.workflow',    # uses the workflow engine
	    'leavedemo.leave',            # the leave application
	)

2. Specific settings:

	WF_APPS_PREFIX = 'leavedemo'
This is the url prefix for workflow application definition;
for example, in the workflow definition the application "app1" is
mapped on the url "/leavedemo/app1"
	
	WF_PUSH_APPS_PREFIX = 'leavedemo.leave.pushapplications'
this is the module containing the push applications functions;
for example, the push application "pushapp1" is a function defined as
following in the leavedemo/leave/pushapplications.py module:
	def pushapp1(workitem):
		...
		return aUser

urls.py:
--------

1. Starting a workflow instance:

the "start_application" is a handler that display a form used to create an instance of the workflow process:

usage:
    (r'^leavedemo/request/$', 'django.contrib.workflow.applications.start_application', {'process_name':'leave',
                                                                                         'form_class':RequestForm,
                                                                                         'template':'start_leave.html'}),

    (r'^leavedemo/checkstatus/$', 'django.contrib.workflow.applications.application_form', {'form_class':ApprovalForm,
                                                                                               'template':'checkstatus.html',
                                                                                               'submit_name':'approval'}),
    (r'^leavedemo/refine/$', 'django.contrib.workflow.applications.application_form', {'form_class':RequestForm,
                                                                                          'template':'refine.html'}),
    (r'^leavedemo/approvalform/$', 'django.contrib.workflow.applications.application_form', {'form_class':ApprovalForm,
                                                                                               'template':'approval.html',
                                                                                               'submit_name':'approval'}),
    (r'^leavedemo/hrform/$', 'django.contrib.workflow.applications.simple_application', {'template':'hrform.html'}),
    (r'^leavedemo/finalinfo/$', 'django.contrib.workflow.applications.simple_application', {'template':'finalinfo.html'}),
    
    (r'^leavedemo/admin/(leave)/(leaverequest)/start/$', 'django.contrib.workflow.applications.start_application_model', {'process_name':'leave'}),

    (r'^leavedemo/admin/', include('django.contrib.admin.urls')),
    (r'^leavedemo/', include('django.contrib.workflow.urls')),



