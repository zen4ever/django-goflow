from django.contrib import admin
from models import *

class SampleModelAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'text', 'requester', 'number',)
admin.site.register(SampleModel, SampleModelAdmin)
