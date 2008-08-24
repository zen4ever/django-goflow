from django.contrib import admin
from models import *

class ProcessInstanceAdmin(admin.ModelAdmin):
    date_hierarchy = 'creationTime'
    list_display = ('title', 'process', 'user', 'creationTime', 'status', 'workitems_list')
    list_filter = ('process', 'status', 'user')
    fieldsets = (
              (None, {'fields':(
                                'title', 'process', 'user',
                                ('status', 'old_status'),
                                'condition',
                                ('object_id', 'content_type'))
                     }),
              )
admin.site.register(ProcessInstance, ProcessInstanceAdmin)


class WorkItemAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'user', 'instance', 'activity', 'status', 'events_list')
    list_filter = ('status', 'user', 'activity',)
    fieldsets = (
              (None, {'fields':(
                                ('instance', 'activity'),
                                'user',
                                'workitem_from',
                                ('status', 'blocked', 'priority'),
                                'push_roles', 'pull_roles')
                     }),
              )
admin.site.register(WorkItem, WorkItemAdmin)


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'name', 'workitem')
admin.site.register(Event, EventAdmin)
