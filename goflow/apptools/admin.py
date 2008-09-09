from django.contrib import admin
from models import *
from goflow.workflow.models import Transition
from goflow.workflow.admin import TransitionAdmin as TransitionAdminOld

class ImageAdmin(admin.ModelAdmin):
    list_display = ('category', 'graphic', 'file', 'url')
    list_filter = ('category',)
admin.site.register(Image, ImageAdmin)

class IconAdmin(admin.ModelAdmin):
    list_display = ('category', 'graphic', 'url')
    list_filter = ('category',)
admin.site.register(Icon, IconAdmin)

class ImageButtonAdmin(admin.ModelAdmin):
    raw_id_fields = ('icon',)
    list_display = ('action', 'label', 'graphic')
admin.site.register(ImageButton, ImageButtonAdmin)
