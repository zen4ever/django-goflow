from django.contrib import admin
from models import *

class ProcessInstanceAdmin(admin.ModelAdmin):
    date_hierarchy = 'creationTime'
    list_display = ('title', 'process', 'user', 'creationTime', 'status')
    list_filter = ('process', 'user')
admin.site.register(ProcessInstance, ProcessInstanceAdmin)


class WorkItemAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'user', 'instance', 'activity', 'status',)
    list_filter = ('user', 'activity', 'status')
admin.site.register(WorkItem, WorkItemAdmin)


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'name', 'workitem')
admin.site.register(Event, EventAdmin)
