from django.contrib import admin
from models import *
from goflow.workflow.models import Transition
from goflow.workflow.admin import TransitionAdmin as TransitionAdminOld


class TransitionIconInline(admin.StackedInline):
    model = TransitionIcon
    max_num = 1
    raw_id_fields = ('icon',)
    fieldsets = (
              (None, {'fields':('label', 'icon',)}),
              )

class ImageAdmin(admin.ModelAdmin):
    list_display = ('category', 'graphic', 'file', 'url')
    list_filter = ('category',)
admin.site.register(Image, ImageAdmin)

class IconAdmin(admin.ModelAdmin):
    list_display = ('category', 'graphic', 'url')
    list_filter = ('category',)
admin.site.register(Icon, IconAdmin)

admin.site.unregister(Transition)

class TransitionAdmin(TransitionAdminOld):
    inlines = [TransitionIconInline]
admin.site.register(Transition, TransitionAdmin)

